import pytest
from src.bot import app as bot


@pytest.fixture
def app():
    yield bot


@pytest.fixture
def client(app):
    return app.test_client()


def test_predict_invalid_method(app, client):
    res = client.get('/')
    assert res.status_code == 405
