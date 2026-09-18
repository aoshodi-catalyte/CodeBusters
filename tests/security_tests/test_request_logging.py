import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from utils.logging_config import configure_logging


def test_request_logging_records_method_path_and_status(
    monkeypatch,
    caplog,
):
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    configure_logging()

    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "ok"}

    from main import log_requests

    app.middleware("http")(log_requests)

    with caplog.at_level(logging.INFO):
        client = TestClient(app)

        response = client.get("/test")

    assert response.status_code == 200

    assert "GET /test -> 200" in caplog.text
    assert "ms" in caplog.text
