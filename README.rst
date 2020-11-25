Celery Batches
==============

.. image:: https://api.travis-ci.com/clokep/celery-batches.svg?branch=main
    :target: https://travis-ci.com/clokep/celery-batches

.. image:: https://readthedocs.org/projects/celery-batches/badge/?version=latest
    :target: https://celery-batches.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Celery Batches provides a ``Task`` class that allows processing of multiple
Celery task calls together as a list. The buffer of tasks calls is flushed on a
timer and based on the number of queued tasks.

What do I need?
===============

celery-batches version runs on,

- Python (3.6, 3.7, 3.8)
- PyPy3 (7.6)

And is tested with Celery >= 4.4.

If you're running an older version of Python, you need to be running
an older version of celery-batches:

- Python 2.7: celery-batches 0.3 series.
- Python 3.4: celery-batches 0.2 series.
- Python 3.5: celery-batches 0.3 series.

If you're running an older version of Celery, you need to be running
an older version of celery-batches:

- Celery < 4.0: Use `celery.contrib.batches` instead.
- Celery 4.0 - 4.3: celery-batches 0.3 series.

History
=======

Celery Batches was distributed as part of Celery (as ``celery.contrib.batches``)
until Celery 4.0. This project updates the Batches code to maintain compatiblity
with newer versions of Celery and other fixes. See the Changelog for details.

Additionally, this repository includes the full history of the code from
``celery.contrib.batches``, but rewritten to the ``celery_batches/__init__.py``
file.
