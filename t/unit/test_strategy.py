from typing import Any, cast
from unittest.mock import MagicMock

from celery_batches import Batches

from celery import Celery


def _make_batch_task() -> Batches:
    app = Celery("test_batches_strategy", set_as_current=False)

    # Celery's task decorator is untyped, so it returns Any.
    @app.task(base=Batches, flush_every=2, flush_interval=10)
    def dummy(requests: list) -> None:
        return None

    return cast(Batches, dummy)


def _mock_consumer() -> MagicMock:
    consumer = MagicMock()
    consumer.connection_errors = ()
    return consumer


def test_strategy_rearms_flush_timer_after_reconnect() -> None:
    """Strategy() must reset per-consumer state so a reconnect re-arms the timer.

    Regression test for the wedge where, after a broker reconnect, the stale
    flush timer (``self._tref``) stayed set and was never re-armed on the new
    event-loop hub, so the worker stopped flushing batches.
    """
    task = _make_batch_task()

    # Simulate state left over from a previous (now dead) consumer. The mock is
    # typed as Any so that assigning it does not narrow ``_tref`` away from
    # Optional, which would make the ``is None`` assertion below unreachable.
    stale_timer: Any = MagicMock()
    task._tref = stale_timer
    task._buffer.put(MagicMock())
    task._pending.put(MagicMock())
    next(task._count)

    handler = task.Strategy(task, task.app, _mock_consumer())

    # The stale timer is cancelled and cleared so the next message re-arms it
    # via the ``if self._tref is None`` guard in the message handler.
    stale_timer.cancel.assert_called_once_with()
    assert task._tref is None
    # Buffers tied to the old connection are dropped, and the flush counter is
    # reset so flush_every alignment starts fresh.
    assert task._buffer.empty()
    assert task._pending.empty()
    assert next(task._count) == 1
    assert callable(handler)


def test_strategy_without_existing_timer_is_a_noop_reset() -> None:
    """First consumer start (no prior timer) must not raise."""
    task = _make_batch_task()
    assert task._tref is None

    handler = task.Strategy(task, task.app, _mock_consumer())

    assert task._tref is None
    assert callable(handler)
