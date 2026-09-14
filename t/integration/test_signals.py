from collections.abc import Callable
from typing import Any

from celery import Celery, signals
from celery.app.task import Task
from celery.contrib.testing.worker import TestWorkController
from celery.utils.dispatch import Signal
from celery.worker.consumer.consumer import Consumer

from . import _wait_for_ping
from .tasks import add, failing


class SignalCounter:
    def __init__(
        self,
        signal: Signal,
        expected_calls: int,
        callback: Callable[..., None] | None = None,
    ):
        self.signal = signal
        signal.connect(self)
        self.calls = 0
        self.expected_calls = expected_calls
        self.callback = callback

    def __call__(self, sender: Task | str | Consumer, **kwargs: Any) -> None:
        if isinstance(sender, Task):
            task_name = sender.name
        elif isinstance(sender, Consumer):
            assert self.signal == signals.task_received
            task_name = kwargs["request"].name
        else:
            task_name = sender

        # Ignore pings, those are used to ensure the worker processes tasks.
        if task_name == "celery.ping":
            return

        self.calls += 1

        # Call the "real" signal, if necessary.
        if self.callback:
            self.callback(sender, **kwargs)

    def assert_calls(self) -> None:
        assert (
            self.calls == self.expected_calls
        ), f"Signal {self.signal.name} called incorrect number of times."


def test_signals(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure that Celery signals run for the batch task."""
    # Configure a SignalCounter for each task signal.
    checks = (
        # Each task request gets published separately.
        (signals.before_task_publish, 2),
        (signals.after_task_publish, 2),
        (signals.task_sent, 2),
        (signals.task_received, 2),
        # The Batch task only runs a single time.
        (signals.task_prerun, 1),
        (signals.task_postrun, 1),
        (signals.task_success, 1),
        # Other task signals are not implemented.
        (signals.task_retry, 0),
        (signals.task_failure, 0),
        (signals.task_revoked, 0),
        (signals.task_internal_error, 0),
        (signals.task_unknown, 0),
        (signals.task_rejected, 0),
    )
    signal_counters = []
    for sig, expected_count in checks:
        counter = SignalCounter(sig, expected_count)
        signal_counters.append(counter)

    # The batch runs after 2 task calls.
    result_1 = add.delay(1)
    result_2 = add.delay(3)

    # Let the worker work.
    _wait_for_ping()

    # Should still have the correct result.
    assert result_1.get() == 4
    assert result_2.get() == 4

    for counter in signal_counters:
        counter.assert_calls()


def test_failure_signal(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure that the task_failure signal fires when a batch task fails."""
    checks = (
        (signals.task_prerun, 1),
        (signals.task_postrun, 1),
        (signals.task_failure, 1),
        (signals.task_success, 0),
    )
    signal_counters = []
    for sig, expected_count in checks:
        counter = SignalCounter(sig, expected_count)
        signal_counters.append(counter)

    # The batch runs after 2 task calls.
    failing.delay()
    failing.delay()

    # Let the worker work.
    _wait_for_ping()

    for counter in signal_counters:
        counter.assert_calls()


def test_current_task(celery_app: Celery, celery_worker: TestWorkController) -> None:
    """Ensure the current_task is properly set when running the task."""

    def signal(sender: Task | str, **kwargs: Any) -> None:
        assert celery_app.current_task.name == "t.integration.tasks.add"

    counter = SignalCounter(signals.task_prerun, 1, signal)

    # The batch runs after 2 task calls.
    result_1 = add.delay(1)
    result_2 = add.delay(3)

    # Let the worker work.
    _wait_for_ping()

    # Should still have the correct result.
    assert result_1.get() == 4
    assert result_2.get() == 4

    counter.assert_calls()
