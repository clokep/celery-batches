from celery import Celery

from celery_batches import Batches

from my_app import User

app = Celery("last_seen")


@app.task(base=Batches, flush_every=100, flush_interval=10)
def last_seen(requests):
    """De-duplicate incoming arguments to only do a task once per input."""
    # Generate a map of unique args -> requests.
    last_seen = {}
    for request in requests:
        user_id, when = request.args
        if user_id not in last_seen or last_seen[user_id] < when:
            last_seen[user_id] = when

    # Update the datastore once per user.
    for user_id, when in last_seen.items():
        User.objects.filter(id=user_id).update(last_logged_in=when)
