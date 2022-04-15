from collections import Counter

from celery import Celery

from celery_batches import Batches

app = Celery("counter")

# Flush after 100 messages, or 10 seconds.
@app.task(base=Batches, flush_every=100, flush_interval=10)
def count_click(requests):
    count = Counter(request.kwargs['url'] for request in requests)
    for url, count in count.items():
        print('>>> Clicks: {0} -> {1}'.format(url, count))
