"""
Ticket service containing all business logic for creating,
updating, and managing quote request tickets.
"""

from typing import Optional, List, Dict
from datetime import datetime
import uuid
from app.database import get_db_client
from app.models.ticket import (
    Ticket, TicketCreate, TicketUpdate, ExtractedData,
    EmailThread, TicketStatus, MockEmailCreate
)
from app.services.claude_extractor import extract_quote_details, generate_followup_email
from app.services.email_service import email_service


def generate_ticket_number() -> str:
    """Generate a unique ticket number."""
    return f"TKT-{uuid.uuid4().hex[:8].upper()}"


def create_ticket_from_email(
    email_body: str,
    email_subject: str,
    customer_email: str,
    email_message_id: Optional[str] = None
) -> Ticket:
    """
    Create a new ticket from an incoming email.

    This function:
    1. Extracts data using Claude
    2. Creates ticket in database
    3. Stores extracted data
    4. Stores email thread
    5. Checks for missing fields
    6. Sends follow-up if needed

    Args:
        email_body: The email content
        email_subject: The email subject
        customer_email: Customer's email address
        email_message_id: Email message ID (optional)

    Returns:
        Created Ticket object
    """

    client = get_db_client()

    # Extract data using Claude
    extracted_data = extract_quote_details(email_body, email_subject)

    # Use extracted email if available, otherwise use provided
    customer_email_final = extracted_data.customer_email or customer_email
    customer_name = extracted_data.customer_name

    # Generate ticket number
    ticket_number = generate_ticket_number()

    # Determine initial status
    missing_fields = extracted_data.get_missing_required_fields()
    if len(missing_fields) == 0:
        status = TicketStatus.READY
    else:
        status = TicketStatus.WAITING_ON_CUSTOMER

    # Create ticket
    result = client.execute(
        """
        INSERT INTO tickets (ticket_number, customer_name, customer_email, status)
        VALUES (?, ?, ?, ?)
        """,
        [ticket_number, customer_name, customer_email_final, status.value]
    )

    ticket_id = result.last_insert_rowid

    # Store extracted data
    client.execute(
        """
        INSERT INTO extracted_data (
            ticket_id, laptop_model, ram, storage, screen_size,
            warranty, quantity, delivery_location, delivery_timeline, budget
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ticket_id,
            extracted_data.laptop_model,
            extracted_data.ram,
            extracted_data.storage,
            extracted_data.screen_size,
            extracted_data.warranty,
            extracted_data.quantity,
            extracted_data.delivery_location,
            extracted_data.delivery_timeline,
            extracted_data.budget
        ]
    )

    # Store incoming email in thread
    client.execute(
        """
        INSERT INTO email_threads (
            ticket_id, email_subject, email_body, direction, email_message_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [ticket_id, email_subject, email_body, "inbound", email_message_id]
    )

    # Send follow-up if fields are missing
    if len(missing_fields) > 0:
        followup = generate_followup_email(
            customer_name or "there",
            missing_fields,
            extracted_data
        )

        # Send follow-up email
        email_result = email_service.send_email(
            to_email=customer_email_final,
            subject=followup["subject"],
            body=followup["body"]
        )

        # Store outbound email in thread
        client.execute(
            """
            INSERT INTO email_threads (
                ticket_id, email_subject, email_body, direction, email_message_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ticket_id,
                followup["subject"],
                followup["body"],
                "outbound",
                email_result.get("message_id")
            ]
        )

    # Return created ticket
    return get_ticket_by_id(ticket_id)


def update_ticket_from_reply(
    ticket_id: int,
    email_body: str,
    email_subject: str,
    email_message_id: Optional[str] = None
) -> Ticket:
    """
    Update an existing ticket from a customer reply.

    This function:
    1. Stores the reply in email thread
    2. Re-extracts data from the entire conversation
    3. Updates ticket with new data
    4. Sends another follow-up if fields still missing

    Args:
        ticket_id: ID of the ticket to update
        email_body: The reply email content
        email_subject: The reply email subject
        email_message_id: Email message ID (optional)

    Returns:
        Updated Ticket object
    """

    client = get_db_client()

    # Get existing ticket
    ticket = get_ticket_by_id(ticket_id)

    if not ticket:
        raise ValueError(f"Ticket {ticket_id} not found")

    # Store incoming reply in thread
    client.execute(
        """
        INSERT INTO email_threads (
            ticket_id, email_subject, email_body, direction, email_message_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [ticket_id, email_subject, email_body, "inbound", email_message_id]
    )

    # Combine all inbound emails for re-extraction
    all_inbound = []
    for thread in ticket.email_threads:
        if thread.direction == "inbound":
            all_inbound.append(thread.email_body)

    combined_email = "\n\n---\n\n".join(all_inbound)

    # Re-extract data with full context
    extracted_data = extract_quote_details(combined_email, email_subject)

    # Update extracted data in database
    client.execute(
        """
        UPDATE extracted_data
        SET laptop_model = ?, ram = ?, storage = ?, screen_size = ?,
            warranty = ?, quantity = ?, delivery_location = ?,
            delivery_timeline = ?, budget = ?
        WHERE ticket_id = ?
        """,
        [
            extracted_data.laptop_model,
            extracted_data.ram,
            extracted_data.storage,
            extracted_data.screen_size,
            extracted_data.warranty,
            extracted_data.quantity,
            extracted_data.delivery_location,
            extracted_data.delivery_timeline,
            extracted_data.budget,
            ticket_id
        ]
    )

    # Update customer name and email if newly extracted
    if extracted_data.customer_name:
        client.execute(
            "UPDATE tickets SET customer_name = ? WHERE id = ?",
            [extracted_data.customer_name, ticket_id]
        )

    if extracted_data.customer_email:
        client.execute(
            "UPDATE tickets SET customer_email = ? WHERE id = ?",
            [extracted_data.customer_email, ticket_id]
        )

    # Check if all fields are now present
    missing_fields = extracted_data.get_missing_required_fields()

    if len(missing_fields) == 0:
        # All fields present, mark as READY
        client.execute(
            "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [TicketStatus.READY.value, ticket_id]
        )
    else:
        # Still missing fields, send another follow-up
        followup = generate_followup_email(
            ticket.customer_name or "there",
            missing_fields,
            extracted_data
        )

        # Send follow-up email
        email_result = email_service.send_email(
            to_email=ticket.customer_email,
            subject=followup["subject"],
            body=followup["body"]
        )

        # Store outbound email in thread
        client.execute(
            """
            INSERT INTO email_threads (
                ticket_id, email_subject, email_body, direction, email_message_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ticket_id,
                followup["subject"],
                followup["body"],
                "outbound",
                email_result.get("message_id")
            ]
        )

        # Update status to WAITING_ON_CUSTOMER
        client.execute(
            "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [TicketStatus.WAITING_ON_CUSTOMER.value, ticket_id]
        )

    # Return updated ticket
    return get_ticket_by_id(ticket_id)


def get_tickets(status: Optional[str] = None) -> List[Ticket]:
    """
    Get all tickets, optionally filtered by status.

    Args:
        status: Optional status filter (NEW, WAITING_ON_CUSTOMER, READY)

    Returns:
        List of Ticket objects
    """

    client = get_db_client()

    if status:
        result = client.execute(
            """
            SELECT id, ticket_number, customer_name, customer_email,
                   status, created_at, updated_at
            FROM tickets
            WHERE status = ?
            ORDER BY created_at DESC
            """,
            [status]
        )
    else:
        result = client.execute(
            """
            SELECT id, ticket_number, customer_name, customer_email,
                   status, created_at, updated_at
            FROM tickets
            ORDER BY created_at DESC
            """
        )

    tickets = []
    for row in result.rows:
        ticket = Ticket(
            id=row[0],
            ticket_number=row[1],
            customer_name=row[2],
            customer_email=row[3],
            status=TicketStatus(row[4]),
            created_at=row[5],
            updated_at=row[6]
        )

        # Load extracted data
        ticket.extracted_data = _get_extracted_data(ticket.id)

        tickets.append(ticket)

    return tickets


def get_ticket_by_id(ticket_id: int) -> Optional[Ticket]:
    """
    Get a single ticket by ID with all related data.

    Args:
        ticket_id: Ticket ID

    Returns:
        Ticket object or None if not found
    """

    client = get_db_client()

    result = client.execute(
        """
        SELECT id, ticket_number, customer_name, customer_email,
               status, created_at, updated_at
        FROM tickets
        WHERE id = ?
        """,
        [ticket_id]
    )

    if not result.rows:
        return None

    row = result.rows[0]
    ticket = Ticket(
        id=row[0],
        ticket_number=row[1],
        customer_name=row[2],
        customer_email=row[3],
        status=TicketStatus(row[4]),
        created_at=row[5],
        updated_at=row[6]
    )

    # Load extracted data
    ticket.extracted_data = _get_extracted_data(ticket.id)

    # Load email threads
    ticket.email_threads = _get_email_threads(ticket.id)

    return ticket


def update_ticket(ticket_id: int, update_data: TicketUpdate) -> Optional[Ticket]:
    """
    Manually update a ticket (used by dashboard).

    Args:
        ticket_id: Ticket ID
        update_data: TicketUpdate object with fields to update

    Returns:
        Updated Ticket object or None if not found
    """

    client = get_db_client()

    # Update tickets table
    if update_data.customer_name is not None:
        client.execute(
            "UPDATE tickets SET customer_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [update_data.customer_name, ticket_id]
        )

    if update_data.customer_email is not None:
        client.execute(
            "UPDATE tickets SET customer_email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [update_data.customer_email, ticket_id]
        )

    if update_data.status is not None:
        client.execute(
            "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [update_data.status.value, ticket_id]
        )

    # Update extracted data if provided
    if update_data.extracted_data is not None:
        ed = update_data.extracted_data
        client.execute(
            """
            UPDATE extracted_data
            SET laptop_model = ?, ram = ?, storage = ?, screen_size = ?,
                warranty = ?, quantity = ?, delivery_location = ?,
                delivery_timeline = ?, budget = ?
            WHERE ticket_id = ?
            """,
            [
                ed.laptop_model, ed.ram, ed.storage, ed.screen_size,
                ed.warranty, ed.quantity, ed.delivery_location,
                ed.delivery_timeline, ed.budget, ticket_id
            ]
        )

    return get_ticket_by_id(ticket_id)


def _get_extracted_data(ticket_id: int) -> Optional[ExtractedData]:
    """Helper to get extracted data for a ticket."""
    client = get_db_client()

    result = client.execute(
        """
        SELECT laptop_model, ram, storage, screen_size, warranty,
               quantity, delivery_location, delivery_timeline, budget
        FROM extracted_data
        WHERE ticket_id = ?
        """,
        [ticket_id]
    )

    if not result.rows:
        return None

    row = result.rows[0]
    return ExtractedData(
        laptop_model=row[0],
        ram=row[1],
        storage=row[2],
        screen_size=row[3],
        warranty=row[4],
        quantity=row[5],
        delivery_location=row[6],
        delivery_timeline=row[7],
        budget=row[8]
    )


def _get_email_threads(ticket_id: int) -> List[EmailThread]:
    """Helper to get email threads for a ticket."""
    client = get_db_client()

    result = client.execute(
        """
        SELECT id, ticket_id, email_subject, email_body, direction,
               email_message_id, in_reply_to, timestamp
        FROM email_threads
        WHERE ticket_id = ?
        ORDER BY timestamp ASC
        """,
        [ticket_id]
    )

    threads = []
    for row in result.rows:
        threads.append(EmailThread(
            id=row[0],
            ticket_id=row[1],
            email_subject=row[2],
            email_body=row[3],
            direction=row[4],
            email_message_id=row[5],
            in_reply_to=row[6],
            timestamp=row[7]
        ))

    return threads


def send_manual_followup(ticket_id: int, subject: str, body: str) -> Dict:
    """
    Manually send a follow-up email for a ticket.

    Args:
        ticket_id: Ticket ID
        subject: Email subject
        body: Email body

    Returns:
        Dict with status
    """

    client = get_db_client()
    ticket = get_ticket_by_id(ticket_id)

    if not ticket:
        return {"success": False, "error": "Ticket not found"}

    # Send email
    email_result = email_service.send_email(
        to_email=ticket.customer_email,
        subject=subject,
        body=body
    )

    # Store in email thread
    client.execute(
        """
        INSERT INTO email_threads (
            ticket_id, email_subject, email_body, direction, email_message_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [ticket_id, subject, body, "outbound", email_result.get("message_id")]
    )

    return email_result
