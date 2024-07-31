import pytest
from unittest.mock import Mock, patch, DEFAULT
from celery import signals
from celery_batches import Batches
from celery_batches.trace import apply_batches_task
from celery.utils.collections import AttributeDict


class TestBatchTask:

    @property
    def request_stack(self):
        class RequestStack:
            def __init__(self, stack):
                self.stack = stack

            def push(self, item):
                self.stack.append(item)

            def pop(self):
                if self.stack:
                    return self.stack.pop()
                return None

        return RequestStack(self._request_stack)

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value):
        self._request = value

    def run(self, requests):
        return [request['id'] for request in requests]


@pytest.fixture
def batch_task():
    tb = TestBatchTask()
    tb._request_stack = []
    tb._request = AttributeDict({'state': None})

    return tb

@pytest.fixture
def simple_request():
    return {
        'id': "test_id",
        'name': "test_task",
        'args': (),
        'kwargs': {},
        'delivery_info': {},
        'hostname': "test_host",
        'ignore_result': False,
        'reply_to': None,
        'correlation_id': None,
        'request_dict': {},
    }


@pytest.fixture(autouse=True)
def setup_signal_receivers():
    def dummy_receiver(*args, **kwargs):
        pass

    signals.task_prerun.connect(dummy_receiver)
    signals.task_postrun.connect(dummy_receiver)
    signals.task_success.connect(dummy_receiver)
    signals.task_failure.connect(dummy_receiver)
    signals.task_revoked.connect(dummy_receiver)

    yield

    signals.task_prerun.disconnect(dummy_receiver)
    signals.task_postrun.disconnect(dummy_receiver)
    signals.task_success.disconnect(dummy_receiver)
    signals.task_failure.disconnect(dummy_receiver)
    signals.task_revoked.disconnect(dummy_receiver)


def test_task_prerun_signal(batch_task, simple_request):
    with patch('celery_batches.trace.send_prerun') as mock_send:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        mock_send.assert_called_once()


def test_task_postrun_signal(batch_task, simple_request):
    with patch('celery_batches.trace.send_postrun') as mock_send:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        mock_send.assert_called_once()


def test_task_success_signal(batch_task, simple_request):
    with patch('celery_batches.trace.send_success') as mock_send:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        mock_send.assert_called_once()


def test_task_failure_signal(batch_task, simple_request):
    def failing_run(requests):
        raise ValueError("Test exception")

    batch_task.run = failing_run

    with patch('celery_batches.trace.send_failure') as mock_send:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        mock_send.assert_called_once()


def test_task_revoked_signal(batch_task, simple_request):
    def revoking_run(requests):
        batch_task.request.state = 'REVOKED'
        return []

    batch_task.run = revoking_run

    with patch('celery_batches.trace.send_revoked') as mock_send:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        mock_send.assert_called_once()


def test_all_signals_sent(batch_task, simple_request):
    with patch.multiple('celery_batches.trace',
                        send_prerun=DEFAULT,
                        send_postrun=DEFAULT,
                        send_success=DEFAULT) as mocks:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        
        for mock in mocks.values():
            mock.assert_called_once()


def test_failure_signals_sent(batch_task, simple_request):
    def failing_run(requests):
        raise ValueError("Test exception")

    batch_task.run = failing_run

    with patch.multiple('celery_batches.trace',
                        send_prerun=DEFAULT,
                        send_postrun=DEFAULT,
                        send_failure=DEFAULT) as mocks:
        apply_batches_task(batch_task, ([simple_request],), 0, None)
        
        for mock in mocks.values():
            mock.assert_called_once()