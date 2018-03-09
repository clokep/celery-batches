# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from time import sleep

from celery.signals import task_prerun, task_postrun

from .tasks import add, cumadd, Results


def test_flush_interval(celery_worker):
    """The batch runs after the flush interval has elapsed."""
    add.delay(1)

    # The flush interval is 1 second, this is longer.
    sleep(2)

    assert Results().get() == 1


def test_flush_calls(celery_worker):
    """The batch runs after two calls."""
    add.delay(1)
    add.delay(3)

    # Yield control to the other thread. (This needs to be shorter than the
    # flush interval.)
    sleep(1)

    assert Results().get() == 4


def test_result(celery_worker):
    result_1 = cumadd.delay(1)
    result_2 = cumadd.delay(2)

    # Yield control to the other thread. (This needs to be shorter than the
    # flush interval.)
    sleep(1)

    assert result_1.get(timeout=3) == 1
    assert result_2.get(timeout=3) == 3


def test_signals(celery_app, celery_worker):
    """The batch runs after two calls."""
    class SignalCounter(object):
        def __init__(self):
            self.calls = 0

        def __call__(self, task_id, task, args, kwargs, **kw):
            self.calls += 1

    prerun = SignalCounter()
    task_prerun.connect(prerun)
    postrun = SignalCounter()
    task_postrun.connect(postrun)

    add.delay(1)
    add.delay(3)

    # Yield control to the other thread. (This needs to be shorter than the
    # flush interval.)
    sleep(1)

    # Should still have the correct result.
    assert Results().get() == 4

    # The task should have only run once.
    assert prerun.calls == 1
    assert postrun.calls == 1


# TODO
# * Test acking
