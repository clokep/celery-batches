from collections.abc import Callable
from datetime import datetime, timedelta
from time import sleep

from celery_batches import Batches, SimpleRequest

from celery import Celery, states
from celery.contrib.testing.worker import TestWorkController
from celery.worker.request import Request

import pytest

from . import _wait_for_ping
from .tasks import add, cumadd


@pytest.mark.usefixtures("depends_on_current_app")
def test_always_eager(celery_app: Celery) -> None:
    """The batch task runs immediately, in the same thread."""
    celery_app.conf.task_always_eager = True
    result = add.delay(1)

    # An EagerResult that resolve to 1 should be returned.
    assert result.get() == 1


def test_apply() -> None:
    """The batch task runs immediately, in the same thread."""
    result = add.apply(args=(1,))

    # An EagerResult that resolve to 1 should be returned.
    assert result.get() == 1


def test_flush_interval(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """The batch task runs after the flush interval has elapsed."""

    if not celery_app.conf.broker_url.startswith("memory"):
        raise pytest.skip("Flaky on live brokers")

    result = add.delay(1)

    # The flush interval is 0.1 second, this is longer.
    sleep(0.2)

    # Let the worker work.
    _wait_for_ping()

    assert result.get() == 1


def test_flush_interval_resets_counter(
    celery_app: Celery, celery_worker: TestWorkController
) -> None:
    """Flush counter is reset after flush is triggered by interval."""

    if not celery_app.conf.broker_url.startswith("memory"):
        raise pytest.skip("Flaky on live brokers")

    result_1 = add.delay(1)

    # The flush interval is 0.1 second, this is longer.
    sleep(2)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get() == 1

    # Run next task, it should not execute as counter was reset
    result_2 = add.delay(2)

    # The flush interval is 0.1 second, this is shorter.
    sleep(0.01)
    _wait_for_ping()

    assert result_2.state == states.PENDING


def test_flush_calls(celery_worker: TestWorkController) -> None:
    """The batch task runs after two calls."""
    result_1 = add.delay(1)
    result_2 = add.delay(3)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get() == 4
    assert result_2.get() == 4


def test_multi_arg(celery_worker: TestWorkController) -> None:
    """The batch task runs after two calls."""
    result_1 = add.delay(1, 2)
    result_2 = add.delay(3, 4)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get() == 10
    assert result_2.get() == 10


def test_kwarg(celery_worker: TestWorkController) -> None:
    """The batch task runs after two calls."""
    result_1 = add.delay(a=1, b=2)
    result_2 = add.delay(a=3, b=4)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get() == 10
    assert result_2.get() == 10


def test_result(celery_worker: TestWorkController) -> None:
    """Each task call can return a result."""
    result_1 = cumadd.delay(1)
    result_2 = cumadd.delay(2)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get(timeout=3) == 1
    assert result_2.get(timeout=3) == 3


def test_acks_early(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure that acking early works properly."""
    # Setup a new task and track which Requests are acked.
    acked = []

    class AckRequest(Request):
        def acknowledge(self) -> None:
            acked.append(self.id)

    @celery_app.task(
        base=Batches, flush_every=2, flush_interval=0.1, Request=AckRequest
    )
    def acks(requests: list[SimpleRequest]) -> None:
        # The tasks are acked before running.
        assert acked == [result_1.id, result_2.id]

    # The task is acking before completion.
    assert acks.acks_late is False

    # Register the task with the worker.
    celery_worker.consumer.update_strategies()

    # Call the tasks, they should ack before flush.
    result_1 = acks.delay()
    result_2 = acks.delay()

    assert acked == []

    # Let the worker work.
    _wait_for_ping()

    # The results are stilled acked after running.
    assert acked == [result_1.id, result_2.id]


def test_acks_late(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure that acking late works properly."""
    # Setup a new task and track which Requests are acked.
    acked = []

    class AckRequest(Request):
        def acknowledge(self) -> None:
            acked.append(self.id)

    @celery_app.task(
        base=Batches,
        acks_late=True,
        flush_every=2,
        flush_interval=0.1,
        Request=AckRequest,
    )
    def acks(requests: list[SimpleRequest]) -> None:
        # When the tasks are running, nothing is acked.
        assert acked == []

    # The task is acking after completion.
    assert acks.acks_late is True

    # Register the task with the worker.
    celery_worker.consumer.update_strategies()

    # Call the tasks, they should ack before flush.
    result_1 = acks.delay()
    result_2 = acks.delay()

    assert acked == []

    # Let the worker work.
    _wait_for_ping()

    # After the tasks are done, both results are acked.
    assert acked == [result_1.id, result_2.id]


def test_countdown(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure that countdowns work properly.

    The batch task handles only the first request initially (as the second request
    is not ready). A subsequent call handles the second request.
    """

    if not celery_app.conf.broker_url.startswith("memory"):
        raise pytest.skip("Flaky on live brokers")

    result_1 = add.apply_async(args=(1,))
    # The countdown is longer than the flush interval + first sleep, but shorter
    # than the flush interval + first sleep + second sleep.
    result_2 = add.apply_async(args=(2,), countdown=3)

    # The flush interval is 0.1 seconds and the retry interval is 0.5 seconds,
    # this is longer.
    sleep(1)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get() == 1
    assert result_2.state == states.PENDING

    sleep(3)

    assert result_2.get() == 2


def test_eta(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure that ETAs work properly."""

    if not celery_app.conf.broker_url.startswith("memory"):
        raise pytest.skip("Flaky on live brokers")

    result_1 = add.apply_async(args=(1,))
    # The countdown is longer than the flush interval + first sleep, but shorter
    # than the flush interval + first sleep + second sleep.
    result_2 = add.apply_async(args=(2,), eta=datetime.utcnow() + timedelta(seconds=3))

    # The flush interval is 0.1 seconds and the retry interval is 0.5 seconds,
    # this is longer.
    sleep(1)

    # Let the worker work.
    _wait_for_ping()

    assert result_1.get() == 1
    assert result_2.state == states.PENDING

    sleep(3)

    assert result_2.get() == 2
