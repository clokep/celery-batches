import pytest

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        # TODO Test both protocol 1 and 2.
        'task_protocol': 1,
    }
