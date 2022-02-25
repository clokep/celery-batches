from celery import shared_task
from celery.utils.log import get_task_logger

from celery_batches import Batches

logger = get_task_logger(__name__)


@shared_task(base=Batches, flush_every=2, flush_interval=1)
def add(requests):
    """Add the first argument of each call."""
    from celery import current_app

    result = 0
    for request in requests:
        result += sum(request.args) + sum(request.kwargs.values())

    for request in requests:
        current_app.backend.mark_as_done(request.id, result, request=request)

    # TODO For EagerResults to work.
    return result


@shared_task(base=Batches, flush_every=2, flush_interval=1)
def cumadd(requests):
    """Calculate the cumulative sum of the first arguments of each call."""
    from celery import current_app

    result = 0
    for request in requests:
        result += request.args[0]
        current_app.backend.mark_as_done(request.id, result, request=request)
