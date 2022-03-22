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

@shared_task(base=Batches, flush_every=2, flush_interval=1)
def retry_if_even(requests):
    """Retry the task if the first argument of a request is even."""
    from celery import current_app

    for request in requests:
        if request.args[0] % 2 == 1:
            # Odd, success
            current_app.backend.mark_as_done(request.id, True, request=request)
        else:
            # Even, so modify to be odd next time around and retry
            current_app.backend.mark_as_failure(request.id, False)
            request.args[0] += 1
            retry_if_even.apply_async(args=request.args, kwargs=request.kwargs, countdown=3)
