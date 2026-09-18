"""Trace task execution.

This module defines how the task execution is traced:
errors are recorded, handlers are applied and so on.

Mimics some of the functionality found in celery.app.trace.trace_task.
"""

import sys
from time import monotonic
from typing import TYPE_CHECKING, Any

from celery import signals, states
from celery._state import _task_stack
from celery.app.task import Context
from celery.utils.log import get_logger
from kombu.utils.uuid import uuid

if TYPE_CHECKING:
    from celery_batches import Batches, SimpleRequest

logger = get_logger(__name__)

send_prerun = signals.task_prerun.send
send_postrun = signals.task_postrun.send
send_success = signals.task_success.send
send_failure = signals.task_failure.send
SUCCESS = states.SUCCESS
FAILURE = states.FAILURE


def apply_batches_task(
    task: "Batches",
    args: tuple[list["SimpleRequest"]],
    loglevel: int,
    logfile: None,
) -> Any:
    request_stack = task.request_stack
    push_request = request_stack.push
    pop_request = request_stack.pop
    push_task = _task_stack.push
    pop_task = _task_stack.pop

    prerun_receivers = signals.task_prerun.receivers
    postrun_receivers = signals.task_postrun.receivers
    success_receivers = signals.task_success.receivers
    failure_receivers = signals.task_failure.receivers

    # Corresponds to multiple requests, so generate a new UUID.
    task_id = uuid()

    push_task(task)
    task_request = Context(loglevel=loglevel, logfile=logfile)
    push_request(task_request)

    result = None
    state = SUCCESS
    runtime = 0.0

    try:
        # -*- PRE -*-
        if prerun_receivers:
            send_prerun(sender=task, task_id=task_id, task=task, args=args, kwargs={})

        # -*- TRACE -*-
        time_start = monotonic()
        try:
            result = task(*args)
            state = SUCCESS
        except Exception as exc:
            result = None
            state = FAILURE
            logger.error("Error: %r", exc, exc_info=True)

            if failure_receivers:
                exc_info = sys.exc_info()
                send_failure(
                    sender=task,
                    task_id=task_id,
                    exception=exc,
                    traceback=exc_info[2],
                    einfo=exc_info,
                )
        else:
            if success_receivers:
                send_success(sender=task, result=result)
        finally:
            runtime = monotonic() - time_start
    finally:
        try:
            if postrun_receivers:
                send_postrun(
                    sender=task,
                    task_id=task_id,
                    task=task,
                    args=args,
                    kwargs={},
                    retval=result,
                    state=state,
                )
        finally:
            pop_task()
            pop_request()

    return result, state, runtime
