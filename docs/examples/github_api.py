import json
from urllib.request import urlopen

from celery import Celery
from celery_batches import Batches

app = Celery("github_api")

emoji_endpoint = 'https://api.github.com/emojis'

@app.task(base=Batches, flush_every=100, flush_interval=10)
def check_emoji(requests):
    supported_emoji = get_supported_emoji()
    # use mark_as_done to manually return response data
    for request in requests:
        response = request.args[0] in supported_emoji
        app.backend.mark_as_done(request.id, supported_emoji, request=request)


def get_supported_emoji():
    response = urlopen(emoji_endpoint)
    # The response is a map of emoji name to image.
    return set(json.load(response))
