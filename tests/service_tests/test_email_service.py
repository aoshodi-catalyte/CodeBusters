import httpx

from services.email_service import EmailService


def test_send_password_reset_code_calls_sendgrid(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

    def fake_post(
        url,
        json,
        headers,
        timeout,
    ):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout

        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "post",
        fake_post,
    )

    service = EmailService(
        api_key="test-api-key",
        from_email="sender@example.com",
    )

    service.send_password_reset_code(
        recipient_email="employee@example.com",
        code="482193",
    )

    assert captured["url"] == (
        "https://api.sendgrid.com/v3/mail/send"
    )

    assert captured["headers"]["Authorization"] == (
        "Bearer test-api-key"
    )

    assert captured["json"]["personalizations"][0]["to"][0]["email"] == (
        "employee@example.com"
    )

    assert captured["json"]["from"]["email"] == (
        "sender@example.com"
    )

    assert captured["json"]["subject"] == (
        "CodeBusters Password Reset"
    )

    assert "482193" in (
        captured["json"]["content"][0]["value"]
    )

    assert captured["timeout"] == 10.0

def test_send_password_reset_code_raises_on_sendgrid_failure(
    monkeypatch,
):
    class FakeResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "SendGrid request failed",
                request=httpx.Request(
                    "POST",
                    "https://api.sendgrid.com/v3/mail/send",
                ),
                response=httpx.Response(500),
            )

    def fake_post(
        url,
        json,
        headers,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "post",
        fake_post,
    )

    service = EmailService(
        api_key="test-api-key",
        from_email="sender@example.com",
    )

    try:
        service.send_password_reset_code(
            recipient_email="employee@example.com",
            code="482193",
        )
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == 500
    else:
        raise AssertionError(
            "Expected SendGrid failure to raise HTTPStatusError"
        )

def test_send_initial_credentials_calls_sendgrid(
    monkeypatch,
):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

    def fake_post(
        url,
        json,
        headers,
        timeout,
    ):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout

        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "post",
        fake_post,
    )

    service = EmailService(
        api_key="test-api-key",
        from_email="sender@example.com",
    )

    service.send_initial_credentials(
        recipient_email="employee@example.com",
        username="yemi.o",
        temporary_password="Temporary123!",
    )

    assert captured["url"] == (
        "https://api.sendgrid.com/v3/mail/send"
    )

    assert captured["headers"]["Authorization"] == (
        "Bearer test-api-key"
    )

    assert captured["json"]["personalizations"][0]["to"][0]["email"] == (
        "employee@example.com"
    )

    assert captured["json"]["from"]["email"] == (
        "sender@example.com"
    )

    assert captured["json"]["subject"] == (
        "Your CodeBusters Account"
    )

    email_content = captured["json"]["content"][0]["value"]

    assert "yemi.o" in email_content
    assert "Temporary123!" in email_content

    assert captured["timeout"] == 10.0


def test_send_initial_credentials_raises_on_sendgrid_failure(
    monkeypatch,
):
    class FakeResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "SendGrid request failed",
                request=httpx.Request(
                    "POST",
                    "https://api.sendgrid.com/v3/mail/send",
                ),
                response=httpx.Response(500),
            )

    def fake_post(
        url,
        json,
        headers,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "post",
        fake_post,
    )

    service = EmailService(
        api_key="test-api-key",
        from_email="sender@example.com",
    )

    try:
        service.send_initial_credentials(
            recipient_email="employee@example.com",
            username="yemi.o",
            temporary_password="Temporary123!",
        )
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == 500
    else:
        raise AssertionError(
            "Expected SendGrid failure to raise HTTPStatusError"
        )
