.. :changelog:

Changelog
#########

0.10 (2025-04-04)
=================

Bugfixes
--------

* Fix installing resetting the count of pending tasks when flushing tasks due to
  the flush interval being reached. (`#95 <https://github.com/clokep/celery-batches/pull/95>`_)

Improvements
------------

* Improve documentation. (`#92 <https://github.com/clokep/celery-batches/pull/92>`_)

Maintenance
-----------

* Support Celery 5.5.
* Drop support for Celery < 5.2. (`#92 <https://github.com/clokep/celery-batches/pull/92>`_)
* Support Python 3.13.
* Drop support for Python 3.8.


0.9 (2024-06-03)
================

Improvements
------------

* Call the task received signal for ``Batches`` task. (`#85 <https://github.com/clokep/celery-batches/pull/85>`_)

Maintenance
-----------

* Limit test requirements to ``pytest-celery~=0.0.0`` for an incompatibility with 1.0.0.
  (`#90 <https://github.com/clokep/celery-batches/pull/90>`_)
* Bump black to 24.3.0. (`#86 <https://github.com/clokep/celery-batches/pull/86>`_)
* Support Celery 5.4. (`#91 <https://github.com/clokep/celery-batches/pull/91>`_)
* Support Python 3.12. (`#91 <https://github.com/clokep/celery-batches/pull/91>`_)


0.8.1 (2023-06-27)
==================

Bugfixes
--------

* Fix installing celery-batches with Celery 5.3. Contributed by `@stegayet <https://github.com/stegayet>`_.
  (`#80 <https://github.com/clokep/celery-batches/pull/80>`_)


0.8 (2023-06-27)
================

Improvements
------------

* Support passing through the `request_dict` from the original Celery request.
  Contributed by `@montasaurus <https://github.com/montasaurus>`_.
  (`#71 <https://github.com/clokep/celery-batches/pull/71>`_)

Maintenance
-----------

* Support Celery 5.3.  Contributed by `@stegayet <https://github.com/stegayet>`_.
  (`#68 <https://github.com/clokep/celery-batches/pull/68>`_,
  `#75 <https://github.com/clokep/celery-batches/pull/75>`_,
  `#77 <https://github.com/clokep/celery-batches/pull/77>`_)
* Drop support for Celery < 5.0. (`#78 <https://github.com/clokep/celery-batches/pull/78>`_)
* Support Python 3.11. (`#75 <https://github.com/clokep/celery-batches/pull/75>`_)
* Drop support for Python 3.7. (`#77 <https://github.com/clokep/celery-batches/pull/77>`_)


0.7 (2022-05-02)
================

Improvements
------------

* Support passing multiple or keyword arguments by disabling Celery's ``typing``
  feature for ``Batches`` tasks. (`#39 <https://github.com/clokep/celery-batches/pull/39>`_)
* Support |using a custom Request class|_ for ``Batches`` tasks.
  (`#63 <https://github.com/clokep/celery-batches/pull/63>`_)
* Support calling tasks with an ``eta`` or ``countdown`` specified. Contributed by
  `@weetster <https://github.com/weetster>`_.
  (`#59 <https://github.com/clokep/celery-batches/pull/59>`_)

Bugfixes
--------

* Handle "hybrid" messages that have moved between Celery versions. Port
  `celery/celery#4358 <https://github.com/celery/celery/pull/4358>`_ to celery-batches.
  (`#64 <https://github.com/clokep/celery-batches/pull/64>`_)
* Fix task ETA issues when timezone is defined in configuration. Port
  `celery/celery#3867 <https://github.com/celery/celery/pull/3867>`_ to celery-batches.
  (`#64 <https://github.com/clokep/celery-batches/pull/64>`_)

.. |using a custom Request class| replace:: using a custom ``Request`` class
.. _using a custom Request class: https://docs.celeryq.dev/en/stable/userguide/tasks.html#requests-and-custom-requests

Maintenance
-----------

* Fix running of tests via tox. (`#40 <https://github.com/clokep/celery-batches/pull/40>`_,
  `#58 <https://github.com/clokep/celery-batches/pull/58>`_)
* Simplify tests. (`#56 <https://github.com/clokep/celery-batches/pull/56>`_,
  `#60 <https://github.com/clokep/celery-batches/pull/60>`_)
* Improve PyPI metadata. (`#43 <https://github.com/clokep/celery-batches/pull/43>`_,
  `#52 <https://github.com/clokep/celery-batches/pull/52>`_)
* Ignore virtualenvs in `.gitignore`. Contributed by `Tony Narlock <https://github.com/tony>`_.
  (`#44 <https://github.com/clokep/celery-batches/pull/44>`_)
* Update README badges to include PyPI and GitHub Actions (instead of Travis CI).
  Contributed by `Tony Narlock <https://github.com/tony>`_.
  (`#47 <https://github.com/clokep/celery-batches/pull/47>`_)
* Update copyright information.  Contributed by `Tony Narlock <https://github.com/tony>`_.
  (`#46 <https://github.com/clokep/celery-batches/pull/46>`_)
* Improve documentation. Contributed by `Tony Narlock <https://github.com/tony>`_.
  (`#45 <https://github.com/clokep/celery-batches/pull/45>`_,
  `#49 <https://github.com/clokep/celery-batches/pull/49>`_,
  `#50 <https://github.com/clokep/celery-batches/pull/50>`_,
  `#55 <https://github.com/clokep/celery-batches/pull/55>`_)
* Document use-cases and include more examples. (`#65 <https://github.com/clokep/celery-batches/pull/65>`_)
* Run the unit tests against RabbitMQ & Redis brokers/backends.
  (`#57 <https://github.com/clokep/celery-batches/pull/57>`_)
* Run `black <https://black.readthedocs.io/>`_, `isort <https://pycqa.github.io/isort/>`_,
  `flake8 <https://flake8.pycqa.org>`_, `pyupgrade <https://github.com/asottile/pyupgrade>`_,
  and `mypy <https://mypy.readthedocs.io>`_.
  (`#61 <https://github.com/clokep/celery-batches/pull/61/>`_,
  `#62 <https://github.com/clokep/celery-batches/pull/62>`_)


0.6 (2021-12-30)
================

Bugfixes
--------

* Fix a bug when passing a ``request`` to ``mark_as_done`` with Celery 5.1.0.
  (`#32 <https://github.com/clokep/celery-batches/pull/32>`_)

Maintenance
-----------

* Clean-up and re-organize code. (`#31 <https://github.com/clokep/celery-batches/pull/31>`_)
* Support Celery 5.2. (`#36 <https://github.com/clokep/celery-batches/pull/36>`_)
* Support Python 3.10. (`#37 <https://github.com/clokep/celery-batches/pull/37>`_)
* Drop support for Python 3.6. (`#36 <https://github.com/clokep/celery-batches/pull/36>`_)
* Changed packaging to use setuptools declarative config in ``setup.cfg``.
  (`#37 <https://github.com/clokep/celery-batches/pull/37>`_)


0.5 (2021-05-24)
================

Bugfixes
--------

* Fix storing of results in the
  `RPC Result Backend <https://docs.celeryproject.org/en/v5.1.0/userguide/tasks.html#rpc-result-backend-rabbitmq-qpid>`_).
  (`#30 <https://github.com/clokep/celery-batches/pull/30>`_)

Maintenance
-----------

* Support Celery 5.1. (`#27 <https://github.com/clokep/celery-batches/pull/27>`_)
* Clean-up unnecessary code. (`#28 <https://github.com/clokep/celery-batches/pull/27>`_)
* CI improvements. (`#25 <https://github.com/clokep/celery-batches/pull/25>`_)


0.4 (2020-11-30)
================

Maintenance
-----------

* Support Celery 5.0. (`#21 <https://github.com/clokep/celery-batches/pull/21>`_)
* Drop support for Celery < 4.4. (`#21 <https://github.com/clokep/celery-batches/pull/21>`_)
* Drop support for Python < 3.6. (`#21 <https://github.com/clokep/celery-batches/pull/21>`_)


0.3 (2020-01-29)
================

Improvements
------------

* Properly set the ``current_task`` when running ``Batches`` tasks. (`#4 <https://github.com/clokep/celery-batches/pull/4>`_)
* Call the success signal after a successful run of the ``Batches`` task. (`#6 <https://github.com/clokep/celery-batches/pull/6>`_)
* Support running tasks eagerly via the ``Task.apply()`` method. This causes
  the task to execute with a batch of a single item. Contributed by
  `@scalen <https://github.com/scalen>`_. (`#16 <https://github.com/clokep/celery-batches/pull/16>`_,
  `#18 <https://github.com/clokep/celery-batches/pull/18>`_)

Maintenance
-----------

* Improved documentation. Contributed by
  `@nijel <https://github.com/nijel>`_. (`#3 <https://github.com/clokep/celery-batches/pull/3>`_,
  `#7 <https://github.com/clokep/celery-batches/pull/7>`_)
* Support Celery 4.2, 4.3, and 4.4. (`#12 <https://github.com/clokep/celery-batches/pull/12>`_,
  `#14 <https://github.com/clokep/celery-batches/pull/14>`_,
  `#19 <https://github.com/clokep/celery-batches/pull/19>`_)
* Support Python 3.7 and 3.8. (`#19 <https://github.com/clokep/celery-batches/pull/19>`_)
* Drop support for Python 3.4. (`#19 <https://github.com/clokep/celery-batches/pull/19>`_)
* CI improvements. (`#5 <https://github.com/clokep/celery-batches/pull/5>`_,
  `#11 <https://github.com/clokep/celery-batches/pull/11>`_,
  `#13 <https://github.com/clokep/celery-batches/pull/13>`_,)


0.2 (2018-04-20)
================

Improvements
------------

* Add support for protocol v2. (`#1 <https://github.com/clokep/celery-batches/pull/1>`_)

Maintenance
-----------

* Add tests. (`#1 <https://github.com/clokep/celery-batches/pull/1>`_,
  `#2 <https://github.com/clokep/celery-batches/pull/2>`_)
* Fixes some documentation issues. (`#1 <https://github.com/clokep/celery-batches/pull/1>`_)


0.1 (2018-03-23)
================

Improvements
------------

* ``Batches`` tasks now call pre- and post-run signals.

Maintenance
-----------

* The initial released version, includes changes to make it a separate package,
  etc.


celery-final
==============

* The final version of ``celery.contrib.batches`` before it was removed in
  |4b3ab708778a3772d24bb39142b7e9d5b94c488b|_.

.. |4b3ab708778a3772d24bb39142b7e9d5b94c488b| replace:: ``4b3ab708778a3772d24bb39142b7e9d5b94c488b``
.. _4b3ab708778a3772d24bb39142b7e9d5b94c488b: https://github.com/celery/celery/commit/4b3ab708778a3772d24bb39142b7e9d5b94c488b
