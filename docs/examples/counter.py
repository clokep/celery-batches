from collections import Counter

from celery_batches import Batches

from celery import Celery

app = Celery("counter")


# Flush after 100 messages, or 10 seconds.
@app.task(base=Batches, flush_every=100, flush_interval=10)
def count_click(requests):
    """Count the number of times each URL is requested."""
    count = Counter(request.kwargs["url"] for request in requests)
    for url, count in count.items():
        print(f">>> Clicks: {url} -> {count}")
