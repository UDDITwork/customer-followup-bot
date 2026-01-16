"""
Unified email service supporting both production (Resend) and development (Mock) modes.
"""

from typing import Optional, Dict, List
from datetime import datetime
import resend
from app.config import settings
from app.database import get_db_client


class EmailService:
    """Unified email service with production and development modes."""

    def __init__(self):
        self.is_production = settings.is_production

        if self.is_production:
            # Initialize Resend for production
            if not settings.resend_api_key:
                raise ValueError("RESEND_API_KEY is required in production mode")
            resend.api_key = settings.resend_api_key

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> Dict:
        """
        Send an email (production via Resend, development via mock).

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (uses default if not provided)

        Returns:
            Dict with status and details
        """

        if self.is_production:
            return self._send_via_resend(to_email, subject, body, from_email)
        else:
            return self._send_via_mock(to_email, subject, body, from_email)

    def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> Dict:
        """Send email via Resend API (production mode)."""

        try:
            from_addr = from_email or settings.resend_from_email

            params = {
                "from": from_addr,
                "to": [to_email],
                "subject": subject,
                "text": body
            }

            response = resend.Emails.send(params)

            return {
                "success": True,
                "message_id": response.get("id"),
                "mode": "production"
            }

        except Exception as e:
            print(f"Error sending email via Resend: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": "production"
            }

    def _send_via_mock(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> Dict:
        """Store email in database instead of sending (development mode)."""

        try:
            from_addr = from_email or settings.resend_from_email or "sales@localhost.dev"

            client = get_db_client()

            # Insert into mock_emails table
            result = client.execute(
                """
                INSERT INTO mock_emails (to_email, from_email, subject, body)
                VALUES (?, ?, ?, ?)
                """,
                [to_email, from_addr, subject, body]
            )

            return {
                "success": True,
                "message_id": f"mock_{result.last_insert_rowid}",
                "mode": "development (mock)",
                "note": "Email stored in database, not actually sent"
            }

        except Exception as e:
            print(f"Error storing mock email: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": "development (mock)"
            }

    def get_mock_emails(self, limit: int = 50) -> List[Dict]:
        """
        Get mock emails from database (development mode only).

        Args:
            limit: Maximum number of emails to return

        Returns:
            List of mock email dictionaries
        """

        if self.is_production:
            return []

        try:
            client = get_db_client()

            result = client.execute(
                """
                SELECT id, to_email, from_email, subject, body, timestamp
                FROM mock_emails
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                [limit]
            )

            emails = []
            for row in result.rows:
                emails.append({
                    "id": row[0],
                    "to": row[1],
                    "from": row[2],
                    "subject": row[3],
                    "body": row[4],
                    "timestamp": row[5]
                })

            return emails

        except Exception as e:
            print(f"Error fetching mock emails: {e}")
            return []

    def clear_mock_emails(self) -> Dict:
        """
        Clear all mock emails (development mode only).

        Returns:
            Dict with status
        """

        if self.is_production:
            return {"success": False, "error": "Not available in production mode"}

        try:
            client = get_db_client()
            client.execute("DELETE FROM mock_emails")

            return {"success": True, "message": "All mock emails cleared"}

        except Exception as e:
            print(f"Error clearing mock emails: {e}")
            return {"success": False, "error": str(e)}


# Create singleton instance
email_service = EmailService()
