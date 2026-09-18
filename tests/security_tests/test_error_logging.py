import logging

from fastapi import FastAPI

from utils.logging_config import configure_logging


def test_unhandled_exception_is_logged(
    monkeypatch,
    caplog,
):
    monkeypatch.setenv(
        "LOG_LEVEL",
        "ERROR",
    )

    configure_logging()

    app = FastAPI()

    @app.get("/failure")
    def failure():
        raise RuntimeError("database connection failed")

    from main import log_requests

    app.middleware("http")(log_requests)

    from fastapi.testclient import TestClient

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    with caplog.at_level(logging.ERROR):
        response = client.get("/failure")

    assert response.status_code == 500

    assert "Unhandled exception during GET /failure" in caplog.text
    assert "database connection failed" in caplog.text
