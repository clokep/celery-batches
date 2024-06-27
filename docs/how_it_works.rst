How it works
############

celery-batches makes no changes to how tasks are created or sent to the broker,
but operates on the workers to process multiple tasks at once. Exactly how tasks
are processed depends on the configuration, but the below assumes usage of the
default `"prefork" configuration`_ of a celery worker (the explanation doesn't
change significantly if the gevent, eventlet, or threads worker pools are used,
but the math is different).

As background, Celery workers have a "main" process which fetches tasks from the
broker. By default it fetches the ":setting:`worker_prefetch_multiplier` x :setting:`worker_concurrency`"
number of tasks (if available). For example, if the prefetch multiplier is 100 and the
concurrency is 4, it attempts to fetch up to 400 items from the broker's queue.
Once in memory the worker deserializes the messages and runs whatever their
:attr:`~celery.app.task.Task.Strategy` is -- for a normal celery
:class:`~celery.app.task.Task` this passes the tasks to the workers in the
processing pool one at a time. (This is the :func:`~celery.worker.strategy.default` strategy.)

The :class:`~celery_batches.Batches` task provides a different strategy which instructs
the "main" celery worker process to queue tasks in memory until either
the :attr:`~celery_batches.Batches.flush_interval` or :attr:`~celery_batches.Batches.flush_every`
is reached and passes that list of tasks to the worker in the processing pool
together.

.. _"prefork" configuration: https://docs.celeryq.dev/en/stable/userguide/workers.html#concurrency
