"""
Twilio Verify SMS service.
"""

import httpx


class SmsService:
    """
    Sends and verifies SMS verification codes through Twilio Verify.
    """

    TWILIO_VERIFY_URL = (
        "https://verify.twilio.com/v2/Services"
    )

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        verify_service_sid: str,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.verify_service_sid = verify_service_sid

    def send_verification(
        self,
        recipient_phone: str,
    ) -> None:
        """
        Start a Twilio Verify SMS verification.

        The verification code is generated and sent by Twilio.
        """

        url = (
            f"{self.TWILIO_VERIFY_URL}/"
            f"{self.verify_service_sid}/Verifications"
        )

        response = httpx.post(
            url,
            data={
                "To": recipient_phone,
                "Channel": "sms",
            },
            auth=(
                self.account_sid,
                self.auth_token,
            ),
            timeout=10.0,
        )

        response.raise_for_status()

    def check_verification(
        self,
        recipient_phone: str,
        code: str,
    ) -> bool:
        """
        Check a verification code through Twilio Verify.

        Returns True when Twilio reports the verification as
        approved and valid. Returns False for an invalid code.
        """

        url = (
            f"{self.TWILIO_VERIFY_URL}/"
            f"{self.verify_service_sid}/VerificationCheck"
        )

        response = httpx.post(
            url,
            data={
                "To": recipient_phone,
                "Code": code,
            },
            auth=(
                self.account_sid,
                self.auth_token,
            ),
            timeout=10.0,
        )

        response.raise_for_status()

        result = response.json()

        return (
            result.get("status") == "approved"
        )
