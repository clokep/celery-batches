import pytest


from celery import Celery, signals
from celery import shared_task
from celery.utils.log import get_task_logger
from typing import List
import sys

from celery_batches import Batches, SimpleRequest

def setup_celery():
    app = Celery('myapp')
    app.conf.broker_url = 'memory://localhost/'
    app.conf.result_backend = 'cache+memory://localhost/'
    print("Created celeery app")
    return app

celery_app = setup_celery()



@celery_app.task(base=Batches, flush_every=2, flush_interval=0.1)
def add(requests: List[SimpleRequest]) -> int:
    """
    Add the first argument of each task.

    Marks the result of each task as the sum.
    """
    print("add")
    result = 0
    for request in requests:
        result += sum(request.args) + sum(request.kwargs.values())

    for request in requests:
        celery_app.backend.mark_as_done(request.id, result, request=request)

    # TODO For EagerResults to work.
    return result

def test_tasks_for_add():
    # current_app.celery_broker_backend = 'memory'
    print("test_tasks_for_add")
    with celery_app.connection_for_write() as connection:
        events_received = [0]

        def handler(event):
            events_received[0] += 1
        
        r = celery_app.events.Receiver(connection,
                                handlers={'*':handler})
        
        result_1 = add.delay(1)
        result_2 = add.delay(2)


        print("READY")
        assert result_1.get() == 3
        assert result_2.get() == 3

        it = r.itercapture(limit=4,wakeup=True)
        next(it)
        assert events_received[0] > 0




