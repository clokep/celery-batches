from celery_batches import Batches

from celery import Celery

from my_app import MyModel

app = Celery("bulk_insert")


@app.task(base=Batches, flush_every=100, flush_interval=10)
def bulk_insert(requests):
    """Insert many rows into a database at once instead of individually."""
    data = []
    for request in requests:
        data.append(MyModel(**request.kwargs))

    # Create all the new rows at once.
    MyModel.objects.bulk_create(data)
