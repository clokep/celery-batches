from celery.contrib.testing.tasks import ping
from celery.result import allow_join_result


def _wait_for_ping(ping_task_timeout: float = 10.0) -> None:
    """
    Wait for the celery worker to respond to a ping.

    This should ensure that any other running tasks are done.
    """
    with allow_join_result():
        assert ping.delay().get(timeout=ping_task_timeout) == "pong"
