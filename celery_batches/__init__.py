"""
celery_batches
==============

Experimental task class that buffers messages and processes them as a list. Task
requests are buffered in memory (on a worker) until either the flush count or
flush interval is reached. Once the requests are flushed, they are sent to the
task as a list of :class:`~celery_batches.SimpleRequest` instances.

It is possible to return a result for each task request by calling
``mark_as_done`` on your results backend. Returning a value from the Batch task
call is only used to provide values to signals and does not populate into the
results backend.

.. warning::

    For this to work you have to set
    :setting:`worker_prefetch_multiplier` to zero, or some value where
    the final multiplied value is higher than ``flush_every``. Note that Celery
    will attempt to continually pull data into memory if this is set to zero.
    This can cause excessive resource consumption on both Celery workers and the
    broker when used with a deep queue.

    In the future we hope to add the ability to direct batching tasks
    to a channel with different QoS requirements than the task channel.

**Simple Example**

A click counter that flushes the buffer every 100 messages, and every
10 seconds.  Does not do anything with the data, but can easily be modified
to store it in a database.

.. code-block:: python

    # Flush after 100 messages, or 10 seconds.
    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def count_click(requests):
        from collections import Counter
        count = Counter(request.kwargs['url'] for request in requests)
        for url, count in count.items():
            print('>>> Clicks: {0} -> {1}'.format(url, count))


Then you can ask for a click to be counted by doing::

    >>> count_click.delay('http://example.com')

**Example returning results**

An interface to the Web of Trust API that flushes the buffer every 100
messages, and every 10 seconds.

.. code-block:: python

    import requests
    from urlparse import urlparse

    from celery_batches import Batches

    wot_api_target = 'https://api.mywot.com/0.4/public_link_json'

    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def wot_api(requests):
        sig = lambda url: url
        reponses = wot_api_real(
            (sig(*request.args, **request.kwargs) for request in requests)
        )
        # use mark_as_done to manually return response data
        for response, request in zip(reponses, requests):
            app.backend.mark_as_done(request.id, response, request=request)


    def wot_api_real(urls):
        domains = [urlparse(url).netloc for url in urls]
        response = requests.get(
            wot_api_target,
            params={'hosts': ('/').join(set(domains)) + '/'}
        )
        return [response.json[domain] for domain in domains]

Using the API is done as follows::

    >>> wot_api.delay('http://example.com')

.. note::

    If you don't have an ``app`` instance then use the current app proxy
    instead::

        from celery import current_app
        current_app.backend.mark_as_done(request.id, response, request=request)

"""
from itertools import count
from queue import Empty, Queue

from celery import signals, states
from celery._state import _task_stack
from celery.app.task import Context, Task
from celery.utils import noop
from celery.utils.log import get_logger
from celery.utils.nodenames import gethostname
from celery.worker.request import Request
from celery.worker.strategy import proto1_to_proto2

from kombu.utils.uuid import uuid


__all__ = ['Batches']

logger = get_logger(__name__)


def consume_queue(queue):
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


send_prerun = signals.task_prerun.send
send_postrun = signals.task_postrun.send
send_success = signals.task_success.send
SUCCESS = states.SUCCESS
FAILURE = states.FAILURE


def apply_batches_task(task, args, loglevel, logfile):
    # Mimics some of the functionality found in celery.app.trace.trace_task.
    request_stack = task.request_stack
    push_request = request_stack.push
    pop_request = request_stack.pop
    push_task = _task_stack.push
    pop_task = _task_stack.pop

    prerun_receivers = signals.task_prerun.receivers
    postrun_receivers = signals.task_postrun.receivers
    success_receivers = signals.task_success.receivers

    # Corresponds to multiple requests, so generate a new UUID.
    task_id = uuid()

    push_task(task)
    task_request = Context(loglevel=loglevel, logfile=logfile)
    push_request(task_request)

    try:
        # -*- PRE -*-
        if prerun_receivers:
            send_prerun(sender=task, task_id=task_id, task=task,
                        args=args, kwargs={})

        # -*- TRACE -*-
        try:
            result = task(*args)
            state = SUCCESS
        except Exception as exc:
            result = None
            state = FAILURE
            logger.error('Error: %r', exc, exc_info=True)
        else:
            if success_receivers:
                send_success(sender=task, result=result)
    finally:
        try:
            if postrun_receivers:
                send_postrun(sender=task, task_id=task_id, task=task,
                             args=args, kwargs={},
                             retval=result, state=state)
        finally:
            pop_task()
            pop_request()

    return result


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
    args = ()

    #: keyword arguments
    kwargs = {}

    #: message delivery information.
    delivery_info = None

    #: worker node name
    hostname = None

    #: used by rpc backend when failures reported by parent process
    reply_to = None

    #: used similarly to reply_to
    correlation_id = None

    #: TODO
    chord = None

    def __init__(self, id, name, args, kwargs, delivery_info, hostname, reply_to, correlation_id):
        self.id = id
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.delivery_info = delivery_info
        self.hostname = hostname
        self.reply_to = reply_to
        self.correlation_id = correlation_id

    @classmethod
    def from_request(cls, request):
        # Support both protocol v1 and v2.
        args, kwargs, embed = request._payload
        return cls(request.id, request.name, args,
                   kwargs, request.delivery_info, request.hostname,
                   request.reply_to, request.correlation_id)


class Batches(Task):
    abstract = True

    #: Maximum number of message in buffer.
    flush_every = 10

    #: Timeout in seconds before buffer is flushed anyway.
    flush_interval = 30

    def __init__(self):
        self._buffer = Queue()
        self._count = count(1)
        self._tref = None
        self._pool = None

    def run(self, requests):
        raise NotImplementedError('must implement run(requests)')

    def Strategy(self, task, app, consumer):
        self._pool = consumer.pool
        hostname = consumer.hostname
        eventer = consumer.event_dispatcher
        Req = Request
        connection_errors = consumer.connection_errors
        timer = consumer.timer
        put_buffer = self._buffer.put
        flush_buffer = self._do_flush

        def task_message_handler(message, body, ack, reject, callbacks, **kw):
            if body is None:
                body, headers, decoded, utc = (
                    message.body, message.headers, False, True,
                )
            else:
                body, headers, decoded, utc = proto1_to_proto2(message, body)

            request = Req(
                message,
                on_ack=ack, on_reject=reject, app=app, hostname=hostname,
                eventer=eventer, task=task,
                body=body, headers=headers, decoded=decoded, utc=utc,
                connection_errors=connection_errors,
            )
            put_buffer(request)

            if self._tref is None:     # first request starts flush timer.
                self._tref = timer.call_repeatedly(
                    self.flush_interval, flush_buffer,
                )

            if not next(self._count) % self.flush_every:
                flush_buffer()

        return task_message_handler

    def apply(self, args=None, kwargs=None, *_args, **_kwargs):
        """
        Execute this task locally as a batch of size 1, by blocking until the task returns.

        Arguments:
            args (Tuple): positional arguments passed on to the task.
        Returns:
            celery.result.EagerResult: pre-evaluated result.
        """
        request = SimpleRequest(
            id=_kwargs.get("task_id", uuid()),
            name="batch request",
            args=args or (),
            kwargs=kwargs or {},
            delivery_info={'is_eager': True},
            hostname=gethostname(),
            reply_to=None,
            correlation_id=None,
        )

        return super().apply(([request],), {}, *_args, **_kwargs)

    def flush(self, requests):
        return self.apply_buffer(requests, ([SimpleRequest.from_request(r)
                                             for r in requests],))

    def _do_flush(self):
        logger.debug('Batches: Wake-up to flush buffer...')
        requests = None
        if self._buffer.qsize():
            requests = list(consume_queue(self._buffer))
            if requests:
                logger.debug('Batches: Buffer complete: %s', len(requests))
                self.flush(requests)
        if not requests:
            logger.debug('Batches: Canceling timer: Nothing in buffer.')
            if self._tref:
                self._tref.cancel()  # cancel timer.
            self._tref = None

    def apply_buffer(self, requests, args=(), kwargs={}):
        acks_late = [], []
        [acks_late[r.task.acks_late].append(r) for r in requests]
        assert requests and (acks_late[True] or acks_late[False])

        def on_accepted(pid, time_accepted):
            [req.acknowledge() for req in acks_late[False]]

        def on_return(result):
            [req.acknowledge() for req in acks_late[True]]

        return self._pool.apply_async(
            apply_batches_task,
            (self, args, 0, None),
            accept_callback=on_accepted,
            callback=acks_late[True] and on_return or noop,
        )
