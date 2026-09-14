from typing import Any

from celery import Celery
from celery.contrib.testing.worker import TestWorkController

from . import _wait_for_ping
from .tasks import add, failing


def filter_events(events: Any, type: str, uuids: set[str]) -> list:
    # publish is called with (event type, event fields as a dict, <other things>.
    #
    # Note that this is called with _other_ events we don't care about (e.g. the
    # ping events), so filter by UUID.
    return [
        {"type": e[0][0], **e[0][1]}
        for e in events
        if e[0][0] == type and e[0][1].get("uuid") in uuids
    ]


def test_events_on_success(capture_events: Any) -> None:
    """Ensure that task-started and task-succeeded events are sent
    per task in a successful batch."""
    result_1 = add.delay(1)
    result_2 = add.delay(3)

    _wait_for_ping()

    assert result_1.get() == 4
    assert result_2.get() == 4

    task_ids = {result_1.id, result_2.id}
    received = filter_events(capture_events.call_args_list, "task-received", task_ids)
    started = filter_events(capture_events.call_args_list, "task-started", task_ids)
    succeeded = filter_events(capture_events.call_args_list, "task-succeeded", task_ids)
    failed = filter_events(capture_events.call_args_list, "task-failed", task_ids)

    # One event per task in the batch.
    assert len(received) == 2, f"Expected 2 task-received events, got {len(received)}"
    assert len(started) == 2, f"Expected 2 task-started events, got {len(started)}"
    assert (
        len(succeeded) == 2
    ), f"Expected 2 task-succeeded events, got {len(succeeded)}"
    assert len(failed) == 0, f"Expected 0 task-failed events, got {len(failed)}"

    # The succeeded events should include a runtime.
    for event in succeeded:
        assert "runtime" in event
        assert event["runtime"] >= 0


def test_events_on_failure(capture_events: Any) -> None:
    """Ensure that task-started and task-failed events are sent
    per task in a failing batch."""
    result_1 = failing.delay()
    result_2 = failing.delay()

    _wait_for_ping()

    task_ids = {result_1.id, result_2.id}
    received = filter_events(capture_events.call_args_list, "task-received", task_ids)
    started = filter_events(capture_events.call_args_list, "task-started", task_ids)
    succeeded = filter_events(capture_events.call_args_list, "task-succeeded", task_ids)
    failed = filter_events(capture_events.call_args_list, "task-failed", task_ids)

    # One event per task in the batch.
    assert len(received) == 2, f"Expected 2 task-received events, got {len(received)}"
    assert len(started) == 2, f"Expected 2 task-started events, got {len(started)}"
    assert (
        len(succeeded) == 0
    ), f"Expected 0 task-succeeded events, got {len(succeeded)}"
    assert len(failed) == 2, f"Expected 2 task-failed events, got {len(failed)}"
