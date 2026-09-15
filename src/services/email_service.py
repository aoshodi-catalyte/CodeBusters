"""
SendGrid email delivery service.
"""

import httpx


class EmailService:
    """
    Sends transactional email through SendGrid.
    """

    SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(
        self,
        api_key: str,
        from_email: str,
    ):
        self.api_key = api_key
        self.from_email = from_email

    def send_password_reset_code(
        self,
        recipient_email: str,
        code: str,
    ) -> None:
        """
        Send a password reset code through SendGrid.
        """

        payload = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": recipient_email,
                        }
                    ]
                }
            ],
            "from": {
                "email": self.from_email,
            },
            "subject": "CodeBusters Password Reset",
            "content": [
                {
                    "type": "text/plain",
                    "value": (
                        "Your CodeBusters password reset code is "
                        f"{code}. This code expires in 10 minutes."
                    ),
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = httpx.post(
            self.SENDGRID_URL,
            json=payload,
            headers=headers,
            timeout=10.0,
        )

        response.raise_for_status()
