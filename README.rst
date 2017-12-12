Celery Batches
==============

Celery Batches provides a ``Task`` class that allows processing of multiple
Celery task calls together as a list. The buffer of tasks calls is flushed on a
timer and based on the number of queued tasks.

History
=======

Celery Batches was part of Celery (as ``celery.contrib.batches``) until Celery
4.0. This is repository includes that history. The Batches code has been updated
to maintain compatible with newer versions of Celery and other fixes. See the
Changelog for details.
