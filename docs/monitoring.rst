Monitoring
##########

:class:`~celery_batches.Batches` tasks emit Celery's standard task events. When
multiple requests are executed as a single batch, each request in the batch
emits its own events.

The following events are emitted, once for each request in the batch:

- **``task-received``** — fires as each task is received by the consumer, with
  the request's ``uuid``, ``name``, ``args``, ``kwargs``, and other request
  metadata.
- **``task-started``** — fires when the batch is accepted by the worker.
- **``task-succeeded``** — fires after the batch completes successfully, with
  ``runtime`` and ``result``.
- **``task-failed``** — fires if the batch raises an exception.

And the following are not currently emitted:

* ``task-sent``
* ``task-rejected``
* ``task-revoked``
* ``task-retried``

.. note::

    Event emission requires two configuration flags:

    - ``worker_send_task_events`` (worker setting) — must be ``True``
    - ``task_send_sent_event`` (task setting) — must be ``True``

    These are typically set in your Celery configuration:

    .. code-block:: python

        app.conf.worker_send_task_events = True
        app.conf.task_send_sent_event = True

.. seealso::

   `Celery documentation on monitoring task events
   <https://docs.celeryq.dev/en/stable/userguide/monitoring.html>`_

   Full details on event fields, signal handlers, and registration of
   receivers are covered in Celery's monitoring documentation. The events
   listed above follow Celery's standard signal format.
