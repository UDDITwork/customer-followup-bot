"""
API routes for email processing (webhooks and development endpoints).
"""

from fastapi import APIRouter, HTTPException, Request, Body
from typing import Dict, List
import json
from app.models.ticket import MockEmailCreate
from app.services import ticket_service
from app.services.email_service import email_service
from app.config import settings
from app.database import find_ticket_by_email_headers

router = APIRouter(tags=["emails"])


@router.post("/webhooks/resend")
async def resend_webhook(request: Request):
    """
    Webhook endpoint for Resend incoming emails (production mode only).

    This endpoint is called by Resend when an email is received.
    """

    if not settings.is_production:
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint only available in production mode"
        )

    try:
        # Parse Resend webhook payload
        payload = await request.json()

        # Log payload for debugging (helps understand Resend's format)
        print(f"[WEBHOOK] Received payload: {json.dumps(payload, indent=2)[:500]}")

        # Extract email details from Resend webhook
        # Handle different possible payload structures
        email_from = payload.get("from", {})
        if isinstance(email_from, dict):
            email_from = email_from.get("email", "")

        email_subject = payload.get("subject", "")
        email_body = payload.get("text", "") or payload.get("html", "")
        message_id = payload.get("message_id", "")

        # Extract threading headers for reply detection
        headers = payload.get("headers", {})
        in_reply_to = payload.get("in_reply_to") or headers.get("in-reply-to") or headers.get("In-Reply-To")
        references = payload.get("references") or headers.get("references") or headers.get("References")

        print(f"[WEBHOOK] Email from: {email_from}, Subject: {email_subject}")
        print(f"[WEBHOOK] In-Reply-To: {in_reply_to}")

        # Check if this is a reply to an existing ticket
        existing_ticket_id = find_ticket_by_email_headers(
            in_reply_to=in_reply_to,
            subject=email_subject,
            customer_email=email_from
        )

        if existing_ticket_id:
            # Reply to existing conversation - update ticket
            print(f"[WEBHOOK] Found existing ticket: {existing_ticket_id}")
            ticket = ticket_service.update_ticket_from_reply(
                ticket_id=existing_ticket_id,
                email_body=email_body,
                email_subject=email_subject
            )

            return {
                "success": True,
                "type": "reply",
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "message": "Ticket updated from customer reply"
            }
        else:
            # New conversation - create new ticket
            print(f"[WEBHOOK] Creating new ticket")
            ticket = ticket_service.create_ticket_from_email(
                email_body=email_body,
                email_subject=email_subject,
                customer_email=email_from,
                email_message_id=message_id
            )

            return {
                "success": True,
                "type": "new_ticket",
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "message": f"New ticket created: {ticket.ticket_number}"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dev/receive-email")
def simulate_receive_email(mock_email: MockEmailCreate):
    """
    Simulate receiving an email (development mode only).

    This endpoint allows you to test the system without sending real emails.

    Body:
    - from_email: Customer's email address
    - subject: Email subject
    - body: Email content
    - in_reply_to: Optional ticket ID if simulating a reply
    """

    if settings.is_production:
        raise HTTPException(
            status_code=404,
            detail="Development endpoints not available in production mode"
        )

    try:
        if mock_email.in_reply_to:
            # This is a reply to an existing ticket
            ticket = ticket_service.update_ticket_from_reply(
                ticket_id=mock_email.in_reply_to,
                email_body=mock_email.body,
                email_subject=mock_email.subject or "Re: Quote Request"
            )

            return {
                "success": True,
                "type": "reply",
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "message": f"Ticket updated from reply"
            }
        else:
            # This is a new email, create a new ticket
            ticket = ticket_service.create_ticket_from_email(
                email_body=mock_email.body,
                email_subject=mock_email.subject or "Quote Request",
                customer_email=mock_email.from_email
            )

            return {
                "success": True,
                "type": "new_ticket",
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "message": f"New ticket created: {ticket.ticket_number}"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dev/sent-emails")
def get_sent_emails(limit: int = 50):
    """
    Get mock sent emails (development mode only).

    Query Parameters:
    - limit: Maximum number of emails to return (default 50)
    """

    if settings.is_production:
        raise HTTPException(
            status_code=404,
            detail="Development endpoints not available in production mode"
        )

    try:
        emails = email_service.get_mock_emails(limit=limit)

        return {
            "success": True,
            "count": len(emails),
            "emails": emails
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dev/sent-emails")
def clear_sent_emails():
    """
    Clear all mock sent emails (development mode only).
    """

    if settings.is_production:
        raise HTTPException(
            status_code=404,
            detail="Development endpoints not available in production mode"
        )

    try:
        result = email_service.clear_mock_emails()

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
