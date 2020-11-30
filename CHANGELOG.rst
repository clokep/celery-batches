.. :changelog:

Changelog
#########

0.4 2020-11-30
==============

* Officially support Celery 5.0. Drop support for Celery < 4.4.
* Drop support for Python < 3.6.

0.3 2020-01-29
==============

* Properly set the ``current_task`` when running Batch tasks.
* Call the success signal after a successful run of the Batch task.
* Support running tasks eagerly via the ``Task.apply()`` method. This causes
  the task to execute with a batch of a single item.
* Officially support Python 3.7 and 3.8. Drop support for Python 3.4.
* Officially support Celery 4.3 and 4.4.

0.2 2018-04-20
==============

* Add support for protocol v2.
* Adds tests.
* Fixes some documentation issues.

0.1 2018-03-23
==============

* The initial released version, includes changes to make it a separate package,
  etc.
* Batch tasks now call pre- and post-run signals.

celery-final
============

* The final version of ``celery.contrib.batches`` before it was removed in
  4b3ab708778a3772d24bb39142b7e9d5b94c488b.
