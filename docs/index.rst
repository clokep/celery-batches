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


.. toctree::
   :hidden:

   examples
   api
   history
