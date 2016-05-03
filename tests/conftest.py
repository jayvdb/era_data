import pytest


@pytest.yield_fixture(scope="session")
def app_config():
    yield None
