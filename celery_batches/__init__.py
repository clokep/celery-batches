from itertools import count
from queue import Empty, Queue
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Iterable,
    List,
    NoReturn,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from celery_batches.trace import apply_batches_task

from celery.app import Celery
from celery.app.task import Task
from celery.concurrency.base import BasePool
from celery.utils import noop
from celery.utils.log import get_logger
from celery.utils.nodenames import gethostname
from celery.worker.consumer import Consumer
from celery.worker.request import Request
from celery.worker.strategy import proto1_to_proto2
from kombu.asynchronous.timer import Timer
from kombu.message import Message
from kombu.utils.uuid import uuid
from vine import promise

__all__ = ["Batches"]

logger = get_logger(__name__)


T = TypeVar("T")


def consume_queue(queue: Queue[T]) -> Iterable[T]:
    """Iterator yielding all immediately available items in a
    :class:`Queue.Queue`.

    The iterator stops as soon as the queue raises :exc:`Queue.Empty`.

    *Examples*

        >>> q = Queue()
        >>> map(q.put, range(4))
        >>> list(consume_queue(q))
        [0, 1, 2, 3]
        >>> list(consume_queue(q))
        []

    """
    get = queue.get_nowait
    while 1:
        try:
            yield get()
        except Empty:
            break


class SimpleRequest:
    """
    A request to execute a task.

    A list of :class:`~celery_batches.SimpleRequest` instances is provided to the
    batch task during execution.

    This must be pickleable (if using the prefork pool), but generally should
    have the same properties as :class:`~celery.worker.request.Request`.
    """

    #: task id
    id = None

    #: task name
    name = None

    #: positional arguments
    args: Tuple[Any, ...] = ()

    #: keyword arguments
    kwargs: Dict[Any, Any] = {}

    #: message delivery information.
    delivery_info = None

    #: worker node name
    hostname = None

    #: if the results of this request should be ignored
    ignore_result = None

    #: used by rpc backend when failures reported by parent process
    reply_to = None

    #: used similarly to reply_to
    correlation_id = None

    #: TODO
    chord = None

    def __init__(
        self,
        id: str,
        name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[Any, Any],
        delivery_info: dict,
        hostname: str,
        ignore_result: bool,
        reply_to: Optional[str],
        correlation_id: Optional[str],
    ):
        self.id = id
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.delivery_info = delivery_info
        self.hostname = hostname
        self.ignore_result = ignore_result
        self.reply_to = reply_to
        self.correlation_id = correlation_id

    @classmethod
    def from_request(cls, request: Request) -> "SimpleRequest":
        # Support both protocol v1 and v2.
        args, kwargs, embed = request._payload
        # Celery 5.1.0 added an ignore_result option.
        ignore_result = getattr(request, "ignore_result", False)
        return cls(
            request.id,
            request.name,
            args,
            kwargs,
            request.delivery_info,
            request.hostname,
            ignore_result,
            request.reply_to,
            request.correlation_id,
        )


class Batches(Task):
    abstract = True

    # Disable typing since the signature of batch tasks take only a single item
    # (the list of SimpleRequest objects), but when calling it it should be
    # possible to provide more arguments.
    #
    # This unfortunately pushes more onto the user to ensure that each call to
    # a batch task is using the expected signature.
    typing = False

    #: Maximum number of message in buffer.
    flush_every = 10

    #: Timeout in seconds before buffer is flushed anyway.
    flush_interval = 30

    def __init__(self) -> None:
        self._buffer: Queue[Request] = Queue()
        self._count = count(1)
        self._tref: Optional[Timer] = None
        self._pool: BasePool = None

    def run(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise NotImplementedError("must implement run(requests)")

    def Strategy(self, task: "Batches", app: Celery, consumer: Consumer) -> Callable:
        # See celery.worker.strategy.default for inspiration.
        #
        # This adds to a buffer at the end, instead of executing the task as
        # the default strategy does.
        self._pool = consumer.pool
        hostname = consumer.hostname
        eventer = consumer.event_dispatcher
        Req = Request
        connection_errors = consumer.connection_errors
        timer = consumer.timer
        put_buffer = self._buffer.put
        flush_buffer = self._do_flush

        def task_message_handler(
            message: Message,
            body: Optional[Dict[str, Any]],
            ack: promise,
            reject: promise,
            callbacks: Set,
            **kw: Any,
        ) -> None:
            if body is None:
                body, headers, decoded, utc = (
                    message.body,
                    message.headers,
                    False,
                    True,
                )
            else:
                body, headers, decoded, utc = proto1_to_proto2(message, body)

            request = Req(
                message,
                on_ack=ack,
                on_reject=reject,
                app=app,
                hostname=hostname,
                eventer=eventer,
                task=task,
                body=body,
                headers=headers,
                decoded=decoded,
                utc=utc,
                connection_errors=connection_errors,
            )
            put_buffer(request)

            if self._tref is None:  # first request starts flush timer.
                self._tref = timer.call_repeatedly(self.flush_interval, flush_buffer)

            if not next(self._count) % self.flush_every:
                flush_buffer()

        return task_message_handler

    def apply(
        self,
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[dict] = None,
        *_args: Any,
        **options: Any,
    ) -> Any:
        """
        Execute the task synchronously as a batch of size 1.

        Arguments:
            args: positional arguments passed on to the task.
        Returns:
            celery.result.EagerResult: pre-evaluated result.
        """
        request = SimpleRequest(
            id=options.get("task_id", uuid()),
            name="batch request",
            args=args or (),
            kwargs=kwargs or {},
            delivery_info={
                "is_eager": True,
                "exchange": options.get("exchange"),
                "routing_key": options.get("routing_key"),
                "priority": options.get("priority"),
            },
            hostname=gethostname(),
            ignore_result=options.get("ignore_result", False),
            reply_to=None,
            correlation_id=None,
        )

        return super().apply(([request],), {}, *_args, **options)

    def _do_flush(self) -> None:
        logger.debug("Batches: Wake-up to flush buffer...")
        requests = None
        if self._buffer.qsize():
            requests = list(consume_queue(self._buffer))
            if requests:
                logger.debug("Batches: Buffer complete: %s", len(requests))
                self.flush(requests)
        if not requests:
            logger.debug("Batches: Canceling timer: Nothing in buffer.")
            if self._tref:
                self._tref.cancel()  # cancel timer.
            self._tref = None

    def flush(self, requests: Collection[Request]) -> Any:
        acks_late: Tuple[List[Request], List[Request]] = [], []
        [acks_late[r.task.acks_late].append(r) for r in requests]  # type: ignore[func-returns-value]
        assert requests and (acks_late[True] or acks_late[False])

        # Ensure the requests can be serialized using pickle for the prefork pool.
        serializable_requests = ([SimpleRequest.from_request(r) for r in requests],)

        def on_accepted(pid: int, time_accepted: float) -> None:
            [req.acknowledge() for req in acks_late[False]]

        def on_return(result: Optional[Any]) -> None:
            [req.acknowledge() for req in acks_late[True]]

        return self._pool.apply_async(
            apply_batches_task,
            (self, serializable_requests, 0, None),
            accept_callback=on_accepted,
            callback=acks_late[True] and on_return or noop,
        )
