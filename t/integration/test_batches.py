# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from time import sleep

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


# TODO
# * Test signals
# * Test acking
