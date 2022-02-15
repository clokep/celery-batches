.. :changelog:

Changelog
#########

next
====

* Support passing multiple or keyword arguments by disabling Celery's ``typing``
  feature for ``Batch`` tasks. (`#39 <https://github.com/clokep/celery-batches/pull/39>`_)
* Fix running of tests via tox. (`#40 <https://github.com/clokep/celery-batches/pull/40>`_)

0.6 2021-12-30
==============

* Fix a bug when passing a ``request`` to ``mark_as_done`` with Celery 5.1.0.
  (`#32 <https://github.com/clokep/celery-batches/pull/32>`_)
* Clean-up and re-organize code. (`#31 <https://github.com/clokep/celery-batches/pull/31>`_)
* Support Celery 5.2. (`#36 <https://github.com/clokep/celery-batches/pull/36>`_)
* Drop support for Python 3.6. (`#36 <https://github.com/clokep/celery-batches/pull/36>`_)
* Support Python 3.10. (`#37 <https://github.com/clokep/celery-batches/pull/37>`_)
* Changed packaging to use setuptools declarative config in ``setup.cfg``.
  (`#37 <https://github.com/clokep/celery-batches/pull/37>`_)

0.5 2021-05-24
==============

* Support Celery 5.1. (`#27 <https://github.com/clokep/celery-batches/pull/27>`_)
* Clean-up unnecessary code. (`#28 <https://github.com/clokep/celery-batches/pull/27>`_)
* Fix storing of results in the
  `RPC Result Backend <https://docs.celeryproject.org/en/v5.1.0/userguide/tasks.html#rpc-result-backend-rabbitmq-qpid>`_).
  (`#30 <https://github.com/clokep/celery-batches/pull/30>`_)
* CI improvements. (`#25 <https://github.com/clokep/celery-batches/pull/25>`_)

0.4 2020-11-30
==============

* Support Celery 5.0. Drop support for Celery < 4.4. (`#21 <https://github.com/clokep/celery-batches/pull/21>`_)
* Drop support for Python < 3.6. (`#21 <https://github.com/clokep/celery-batches/pull/21>`_)

0.3 2020-01-29
==============

* Properly set the ``current_task`` when running ``Batch`` tasks. (`#4 <https://github.com/clokep/celery-batches/pull/4>`_)
* Call the success signal after a successful run of the ``Batch`` task. (`#6 <https://github.com/clokep/celery-batches/pull/6>`_)
* Support running tasks eagerly via the ``Task.apply()`` method. This causes
  the task to execute with a batch of a single item. Contributed by
  `@scalen <https://github.com/scalen>`_. (`#16 <https://github.com/clokep/celery-batches/pull/16>`_,
  `#18 <https://github.com/clokep/celery-batches/pull/18>`_)
* Improved documentation. Contributed by
  `@nijel <https://github.com/nijel>`_. (`#3 <https://github.com/clokep/celery-batches/pull/3>`_,
  `#7 <https://github.com/clokep/celery-batches/pull/7>`_)
* Support Python 3.7 and 3.8. Drop support for Python 3.4. (`#19 <https://github.com/clokep/celery-batches/pull/19>`_)
* Support Celery 4.2, 4.3, and 4.4. (`#12 <https://github.com/clokep/celery-batches/pull/12>`_,
  `#14 <https://github.com/clokep/celery-batches/pull/14>`_,
  `#19 <https://github.com/clokep/celery-batches/pull/19>`_)
* CI improvements. (`#5 <https://github.com/clokep/celery-batches/pull/5>`_,
  `#11 <https://github.com/clokep/celery-batches/pull/11>`_,
  `#13 <https://github.com/clokep/celery-batches/pull/13>`_,)

0.2 2018-04-20
==============

* Add support for protocol v2. (`#1 <https://github.com/clokep/celery-batches/pull/1>`_)
* Add tests. (`#1 <https://github.com/clokep/celery-batches/pull/1>`_,
  `#2 <https://github.com/clokep/celery-batches/pull/2>`_)
* Fixes some documentation issues. (`#1 <https://github.com/clokep/celery-batches/pull/1>`_)

0.1 2018-03-23
==============

* The initial released version, includes changes to make it a separate package,
  etc.
* Batch tasks now call pre- and post-run signals.

celery-final
============

* The final version of ``celery.contrib.batches`` before it was removed in
  4b3ab708778a3772d24bb39142b7e9d5b94c488b.
