##############
celery-batches
##############

Experimental task class that buffers messages and processes them as a list. Task
requests are buffered in memory (on a worker) until either the flush count or
flush interval is reached. Once the requests are flushed, they are sent to the
task as a list of :class:`~celery_batches.SimpleRequest` instances.

It is possible to return a result for each task request by calling
``mark_as_done`` on your results backend. Returning a value from the Batch task
call is only used to provide values to signals and does not populate into the
results backend.

.. warning::

    For this to work you have to set
    :setting:`worker_prefetch_multiplier` to zero, or some value where
    the final multiplied value is higher than ``flush_every``. Note that Celery
    will attempt to continually pull data into memory if this is set to zero.
    This can cause excessive resource consumption on both Celery workers and the
    broker when used with a deep queue.

    In the future we hope to add the ability to direct batching tasks
    to a channel with different QoS requirements than the task channel.

**Simple Example**

A click counter that flushes the buffer every 100 messages, and every
10 seconds.  Does not do anything with the data, but can easily be modified
to store it in a database.

.. code-block:: python

    # Flush after 100 messages, or 10 seconds.
    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def count_click(requests):
        from collections import Counter
        count = Counter(request.kwargs['url'] for request in requests)
        for url, count in count.items():
            print('>>> Clicks: {0} -> {1}'.format(url, count))


Then you can ask for a click to be counted by doing::

    >>> count_click.delay('http://example.com')

**Example returning results**

An interface to the Web of Trust API that flushes the buffer every 100
messages, and every 10 seconds.

.. code-block:: python

    import requests
    from urlparse import urlparse

    from celery_batches import Batches

    wot_api_target = 'https://api.mywot.com/0.4/public_link_json'

    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def wot_api(requests):
        sig = lambda url: url
        reponses = wot_api_real(
            (sig(*request.args, **request.kwargs) for request in requests)
        )
        # use mark_as_done to manually return response data
        for response, request in zip(reponses, requests):
            app.backend.mark_as_done(request.id, response, request=request)


    def wot_api_real(urls):
        domains = [urlparse(url).netloc for url in urls]
        response = requests.get(
            wot_api_target,
            params={'hosts': ('/').join(set(domains)) + '/'}
        )
        return [response.json[domain] for domain in domains]

Using the API is done as follows::

    >>> wot_api.delay('http://example.com')

.. note::

    If you don't have an ``app`` instance then use the current app proxy
    instead::

        from celery import current_app
        current_app.backend.mark_as_done(request.id, response, request=request)


API
---

.. currentmodule:: celery_batches

.. automodule:: celery_batches

    **API**

    .. autoclass:: Batches
        :members:
        :undoc-members:
    .. autoclass:: SimpleRequest
        :members:
        :undoc-members:

Additional notes
----------------

.. toctree::
   :maxdepth: 2

   history
