import pytest
from celery import Celery
from celery_batches import Batches, SimpleRequest
from typing import List
import asyncio
import logging


pytest_plugins = ('pytest_asyncio',)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_celery():
    app = Celery('myapp')
    app.conf.update(
        broker_url='memory://',
        result_backend='cache+memory://',
        task_always_eager=False,
        worker_concurrency=1,
        worker_prefetch_multiplier=1,
        task_create_missing_queues=True,
        broker_connection_retry_on_startup=True,
    )
    return app


celery_app = setup_celery()


@celery_app.task(base=Batches, flush_every=2, flush_interval=0.1)
def add(requests: List[SimpleRequest]) -> int:
    """
    Add the first argument of each task.

    Marks the result of each task as the sum.
    """
    logger.debug(f"Processing {len(requests)} requests")
    result = sum(
        sum(request.args) + sum(request.kwargs.values())
        for request in requests
    )

    for request in requests:
        celery_app.backend.mark_as_done(request.id, result, request=request)

    logger.debug(f"Finished processing. Result: {result}")
    return result


@pytest.mark.asyncio
async def test_tasks_for_add(celery_worker):
    logger.debug("Starting test_tasks_for_add")

    # Send tasks
    logger.debug("Sending tasks")
    result_1 = add.delay(1)
    result_2 = add.delay(2)

    logger.debug("Waiting for results")
    try:
        # Wait for the batch to be processed
        results = await asyncio.wait_for(asyncio.gather(
            asyncio.to_thread(result_1.get),
            asyncio.to_thread(result_2.get)
        ), timeout=5.0)
        logger.debug(f"Results: {results}")
    except asyncio.TimeoutError:
        logger.error("Test timed out while waiting for results")
        pytest.fail("Test timed out while waiting for results")

    # Check results
    assert results[0] == 3, f"Expected 3, got {results[0]}"
    assert results[1] == 3, f"Expected 3, got {results[1]}"

    logger.debug("Test completed successfully")
