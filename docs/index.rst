##############
celery-batches
##############

celery-batches is a task class that buffers messages and processes them as a list. Task
requests are buffered in memory (on a worker) until either the flush count or
flush interval is reached. Once the requests are flushed, they are sent to the
task as a list of :class:`~celery_batches.SimpleRequest` instances.

Some potential use-cases for batching of task calls include:

* De-duplicating tasks.
* Accumulating / only handling the latest task with similar arguments.
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

Retrying tasks
##############

In order to retry a failed task, the task must be re-executed with the original
``task_id``, see the example below:

.. code-block:: python

    @app.task(base=Batches, flush_every=100, flush_interval=10)
    def flaky_task(requests):
        for request in requests:
            # Do something that might fail.
            try:
                response = might_fail(*request.args, **request.kwargs)
            except TemporaryError:
                # Retry the task 10 seconds from now with the same arguments and task_id.
                flaky_task.apply_async(
                    args=request.args,
                    kwargs=request.kwargs,
                    countdown=10,
                    task_id=request.id,
                )
            else:
                app.backend.mark_as_done(request.id, response, request=request)

Note that the retried task is still bound by the flush rules of the ``Batches``
task, it is used as a lower-bound and will not run *before* that timeout. In the
example above it will run between 10 - 20 seconds from now, assuming no other
tasks are in the queue.

.. toctree::
   :hidden:

   examples
   api
   history
