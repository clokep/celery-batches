import os

import pytest

TEST_BROKER = os.environ.get("TEST_BROKER", "memory://")
TEST_BACKEND = os.environ.get("TEST_BACKEND", "cache+memory://")


@pytest.fixture(scope="session", params=[1, 2])
def celery_config(request):
    return {
        "broker_url": TEST_BROKER,
        "result_backend": TEST_BACKEND,
        # Test both protocol 1 and 2 via the parameterized fixture.
        "task_protocol": request.param,
    }
