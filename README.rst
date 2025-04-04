Celery Batches
==============

.. image:: https://img.shields.io/pypi/v/celery-batches.svg
    :target: https://pypi.org/project/celery-batches/

.. image:: https://github.com/clokep/celery-batches/actions/workflows/main.yml/badge.svg
    :target: https://github.com/clokep/celery-batches/actions/workflows/main.yml

.. image:: https://readthedocs.org/projects/celery-batches/badge/?version=latest
    :target: https://celery-batches.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Celery Batches provides a ``Task`` class that allows processing of multiple
Celery task calls together as a list. The buffer of tasks calls is flushed on a
timer and based on the number of queued tasks.

Some potential use-cases for batching of task calls include:

* De-duplicating tasks.
* Accumulating / only handling the latest task with similar arguments.
* Bulk inserting / updating of data.
* Tasks with expensive setup that can run across a range of arguments.

What do I need?
===============

celery-batches version runs on,

- Python (3.9, 3.10, 3.11, 3.12, 3.13)
- PyPy (3.10, 3.11)

And is tested with Celery ~= 5.0.

If you're running an older version of Python, you need to be running
an older version of celery-batches, the last version supporting each
Python version is listed below:

- Python 2.7: celery-batches 0.3.
- Python 3.4: celery-batches 0.2.
- Python 3.5: celery-batches 0.3.
- Python 3.6: celery-batches 0.5.
- Python 3.7: celery-batches 0.7.
- Python 3.8: celery-batches 0.9.

If you're running an older version of Celery, you need to be running
an older version of celery-batches:

- Celery < 4.0: Use `celery.contrib.batches` instead.
- Celery 4.0 - 4.3: celery-batches 0.3.
- Celery 4.4: celery-batches 0.7.
- Celery 5.0 - 5.1: celery-batches 0.9.

History
=======

Celery Batches was distributed as part of Celery (as ``celery.contrib.batches``)
until Celery 4.0. This project updates the Batches code to maintain compatiblity
with newer versions of Celery and other fixes. See the Changelog for details.

Additionally, this repository includes the full history of the code from
``celery.contrib.batches``, but rewritten to the ``celery_batches/__init__.py``
file.
