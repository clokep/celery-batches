import pytest


@pytest.fixture(scope='session', params=[1, 2])
def celery_config(request):
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        # Test both protocol 1 and 2 via the parameterized fixture.
        'task_protocol': request.param,
    }
