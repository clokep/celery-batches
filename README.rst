Celery Batches
==============

Celery Batches provides a ``Task`` class that allows processing of multiple
Celery task calls together as a list. The buffer of tasks calls is flushed on a
timer and based on the number of queued tasks.

History
=======

Celery Batches was distributed as part of Celery (as ``celery.contrib.batches``)
until Celery 4.0. This project updates the Batches code to maintain compatiblity
with newer versions of Celery and other fixes. See the Changelog for details.

Additionally, this is repository includes the full history of the code from
``celery.contrib.batches``, but rewritten to the ``celery_batches/__init__.py``
file.
