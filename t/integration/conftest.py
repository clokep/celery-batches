import os
from typing import Any
from unittest.mock import patch

from celery.contrib.testing.worker import TestWorkController

import pytest
from _pytest.fixtures import SubRequest

TEST_BROKER = os.environ.get("TEST_BROKER", "memory://")
TEST_BACKEND = os.environ.get("TEST_BACKEND", "cache+memory://")


@pytest.fixture(scope="session", params=[1, 2])
def celery_config(request: SubRequest) -> dict[str, Any]:
    return {
        "broker_url": TEST_BROKER,
        "result_backend": TEST_BACKEND,
        # Test both protocol 1 and 2 via the parameterized fixture.
        "task_protocol": request.param,
        "worker_send_task_events": True,
        "task_send_sent_event": True,
    }


@pytest.fixture
def capture_events(celery_worker: TestWorkController) -> Any:
    """Patch ``publish`` and disable task-event buffering.

    The worker buffers ``task``-group events only on async transports
    (e.g. Redis), then flushes them via the producer, which bypasses
    ``publish``. Clearing ``buffer_group`` makes ``send`` publish the
    events immediately so the mock observes them. This is safe even
    though ``Batches.Strategy`` captures ``send_event`` at setup time:

    ``send`` resolves ``self.publish`` dynamically at call time.
    """
    dispatcher = celery_worker.consumer.event_dispatcher  # type: ignore[attr-defined]
    if dispatcher and dispatcher.buffer_group:
        dispatcher.buffer_group = frozenset()
    with patch.object(dispatcher, "publish") as publish:
        yield publish
