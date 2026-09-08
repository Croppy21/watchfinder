import os

from dotenv import load_dotenv
import resend


load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_password_reset_email(
    recipient_email: str,
    reset_url: str
):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient_email,
        "subject": "Reset your WatchFinder password",
        "html": f"""
            <h2>Reset your WatchFinder password</h2>

            <p>We received a request to reset your WatchFinder password.</p>

            <p>
                <a href="{reset_url}">
                    Reset your password
                </a>
            </p>

            <p>
                This link will expire in 1 hour and can only be used once.
            </p>

            <p>
                If you didn't request a password reset, you can safely
                ignore this email.
            </p>

            <p>— WatchFinder</p>
        """
    })