########
Examples
########

Simple Example
##############

A click counter that flushes the buffer every 100 messages, and every
10 seconds.  Does not do anything with the data, but can easily be modified
to store it in a database.

.. code-block:: python

    from collections import Counter

    # Flush after 100 messages, or 10 seconds.
    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def count_click(requests):
        count = Counter(request.kwargs['url'] for request in requests)
        for url, count in count.items():
            print('>>> Clicks: {0} -> {1}'.format(url, count))


Then you can ask for a click to be counted by doing::

    >>> count_click.delay(url='http://example.com')

Example returning results
#########################

An interface to the GitHub API that avoids requesting the API endpoint for each
task. It flushes the buffer every 100 messages, and every 10 seconds.

.. code-block:: python

    import json
    from urllib.request import urlopen

    from celery_batches import Batches

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

Using the API is done as follows::

    >>> result = check_emoji.delay('celery')
    >>> assert result.get() is False
