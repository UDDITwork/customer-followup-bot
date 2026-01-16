"""
API routes for ticket management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.models.ticket import Ticket, TicketUpdate
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/", response_model=List[Ticket])
def list_tickets(status: Optional[str] = Query(None, description="Filter by status")):
    """
    Get all tickets, optionally filtered by status.

    Query Parameters:
    - status: Optional status filter (NEW, WAITING_ON_CUSTOMER, READY)
    """
    try:
        tickets = ticket_service.get_tickets(status=status)
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int):
    """
    Get a single ticket by ID with all details including email thread.
    """
    ticket = ticket_service.get_ticket_by_id(ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.patch("/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: int, update_data: TicketUpdate):
    """
    Update a ticket (manual edits from dashboard).

    Allows updating:
    - Customer name and email
    - Ticket status
    - Extracted data fields
    """
    ticket = ticket_service.update_ticket(ticket_id, update_data)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.post("/{ticket_id}/send-email")
def send_followup(
    ticket_id: int,
    subject: str = Query(..., description="Email subject"),
    body: str = Query(..., description="Email body")
):
    """
    Manually send a follow-up email for a ticket.
    """
    result = ticket_service.send_manual_followup(ticket_id, subject, body)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result
