import httpx

from services.sms_service import SmsService


def test_send_verification_starts_sms_verification(
    monkeypatch,
):
    captured = {}

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "sid": "VE123",
                "status": "pending",
            }

    def fake_post(
        url,
        data=None,
        headers=None,
        timeout=None,
        auth=None,
    ):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        captured["timeout"] = timeout
        captured["auth"] = auth

        return FakeResponse()

    monkeypatch.setattr(
        "services.sms_service.httpx.post",
        fake_post,
    )

    service = SmsService(
        account_sid="AC123",
        auth_token="test-auth-token",
        verify_service_sid="VA123",
    )

    service.send_verification(
        "+13125551234",
    )

    assert captured["url"] == (
        "https://verify.twilio.com/v2/"
        "Services/VA123/Verifications"
    )

    assert captured["data"] == {
        "To": "+13125551234",
        "Channel": "sms",
    }

    assert captured["auth"] == (
        "AC123",
        "test-auth-token",
    )

    assert captured["timeout"] == 10.0


def test_check_verification_returns_true_when_approved(
    monkeypatch,
):
    captured = {}

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "sid": "VE123",
                "status": "approved",
            }

    def fake_post(
        url,
        data=None,
        headers=None,
        timeout=None,
        auth=None,
    ):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        captured["timeout"] = timeout
        captured["auth"] = auth

        return FakeResponse()

    monkeypatch.setattr(
        "services.sms_service.httpx.post",
        fake_post,
    )

    service = SmsService(
        account_sid="AC123",
        auth_token="test-auth-token",
        verify_service_sid="VA123",
    )

    result = service.check_verification(
        "+13125551234",
        "482193",
    )

    assert result is True

    assert captured["url"] == (
        "https://verify.twilio.com/v2/"
        "Services/VA123/VerificationCheck"
    )

    assert captured["data"] == {
        "To": "+13125551234",
        "Code": "482193",
    }

    assert captured["auth"] == (
        "AC123",
        "test-auth-token",
    )

    assert captured["timeout"] == 10.0


def test_check_verification_returns_false_when_not_approved(
    monkeypatch,
):
    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "sid": "VE123",
                "status": "pending",
            }

    monkeypatch.setattr(
        "services.sms_service.httpx.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    service = SmsService(
        account_sid="AC123",
        auth_token="test-auth-token",
        verify_service_sid="VA123",
    )

    result = service.check_verification(
        "+13125551234",
        "111111",
    )

    assert result is False


def test_send_verification_raises_when_twilio_returns_error(
    monkeypatch,
):
    def fake_post(
        *args,
        **kwargs,
    ):
        request = httpx.Request(
            "POST",
            "https://verify.twilio.com/v2/"
            "Services/VA123/Verifications",
        )

        return httpx.Response(
            401,
            request=request,
        )

    monkeypatch.setattr(
        "services.sms_service.httpx.post",
        fake_post,
    )

    service = SmsService(
        account_sid="AC123",
        auth_token="bad-token",
        verify_service_sid="VA123",
    )

    try:
        service.send_verification(
            "+13125551234",
        )
    except httpx.HTTPStatusError:
        pass
    else:
        raise AssertionError(
            "Expected Twilio HTTP error."
        )
