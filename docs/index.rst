##############
celery-batches
##############

celery-batches is a task class that buffers messages and processes them as a list. Task
requests are buffered in memory (on a worker) until either the flush count or
flush interval is reached. Once the requests are flushed, they are sent to the
task as a list of :class:`~celery_batches.SimpleRequest` instances.

Some potential use-cases for batching of task calls include:

* De-duplicating tasks.
* Accumlating / only handling the latest task with similar arguments.
* Bulk inserting / updating of data.
* Tasks with expensive setup that can run across a range of arguments.

For the ``Batches`` task to work properly you must configure :setting:`worker_prefetch_multiplier`
to zero, or some value where the final multiplied value is higher than ``flush_every``.

.. warning::

    Celery will attempt to continually pull all data from a queue into memory if
    :setting:`worker_prefetch_multiplier` is set to zero. This can cause excessive
    resource consumption on both Celery workers and the broker when used with a
    deep queue.

In the future we hope to add the ability to direct batching tasks
to a channel with different QoS requirements than the task channel.

Returning results
#################

It is possible to return a result for each task request by calling ``mark_as_done``
on your results backend. Returning a value from the ``Batches`` task call is only
used to provide values to signals and does not populate into the results backend.

.. note::

    If you don't have an ``app`` instance then use the current app proxy
    instead:

    .. code-block:: python

        from celery import current_app
        current_app.backend.mark_as_done(request.id, response, request=request)

.. note::

    In order to retry a failed task, the task must be re-executed with a matching ``task_id``,
    as shown below::

        @app.task(base=Batches, flush_every=100, flush_interval=10)
        def wot_api(requests):
            # Do things that might fail
            # responses = [...]

            for response, request in zip(reponses, requests):
                if response is True:
                    app.backend.mark_as_done(request.id, response, request=request)
                else:
                    # Retry the task with the same arguments and task_id, 10 seconds from now
                    wot_api.apply_async(
                        args=request.args,
                        kwargs=request.kwargs,
                        countdown=10,
                        task_id=request.id,
                    )

.. toctree::
   :hidden:

   examples
   api
   history
