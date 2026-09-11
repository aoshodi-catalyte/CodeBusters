"""
Twilio SMS delivery service.
"""

from base64 import b64encode

import httpx


class SmsService:
    """
    Sends SMS messages through Twilio.
    """

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_phone: str,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_phone = from_phone

    def send_password_reset_code(
        self,
        recipient_phone: str,
        code: str,
    ) -> None:
        """
        Send a password reset code through Twilio.
        """

        url = (
            "https://api.twilio.com/2010-04-01/"
            f"Accounts/{self.account_sid}/Messages.json"
        )

        body = {
            "To": recipient_phone,
            "From": self.from_phone,
            "Body": (
                "Your CodeBusters password reset code is "
                f"{code}. This code expires in 10 minutes."
            ),
        }

        auth_value = b64encode(
            f"{self.account_sid}:{self.auth_token}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth_value}",
        }

        response = httpx.post(
            url,
            data=body,
            headers=headers,
            timeout=10.0,
        )

        response.raise_for_status()
