"""
Pydantic models for tickets, extracted data, and email threads.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TicketStatus(str, Enum):
    """Ticket status enum."""
    NEW = "NEW"
    WAITING_ON_CUSTOMER = "WAITING_ON_CUSTOMER"
    READY = "READY"


class ExtractedData(BaseModel):
    """Extracted quote request data."""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    laptop_model: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    screen_size: Optional[str] = None
    warranty: Optional[str] = None
    quantity: Optional[str] = None
    delivery_location: Optional[str] = None
    delivery_timeline: Optional[str] = None
    budget: Optional[str] = None

    def get_missing_required_fields(self) -> List[str]:
        """
        Get list of missing required fields.
        Budget is optional, all others are required.
        """
        required_fields = [
            "laptop_model", "ram", "storage", "screen_size",
            "warranty", "quantity", "delivery_location", "delivery_timeline"
        ]

        missing = []
        for field in required_fields:
            value = getattr(self, field)
            if not value or value.strip() == "":
                missing.append(field)

        return missing

    def is_complete(self) -> bool:
        """Check if all required fields are present."""
        return len(self.get_missing_required_fields()) == 0


class EmailThread(BaseModel):
    """Email in a ticket thread."""
    id: Optional[int] = None
    ticket_id: int
    email_subject: Optional[str] = None
    email_body: str
    direction: str  # "inbound" or "outbound"
    email_message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    timestamp: Optional[datetime] = None


class Ticket(BaseModel):
    """Ticket model."""
    id: Optional[int] = None
    ticket_number: str
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    status: TicketStatus = TicketStatus.NEW
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related data (not stored in tickets table directly)
    extracted_data: Optional[ExtractedData] = None
    email_threads: Optional[List[EmailThread]] = None


class TicketCreate(BaseModel):
    """Model for creating a new ticket."""
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    extracted_data: ExtractedData
    initial_email_subject: Optional[str] = None
    initial_email_body: str


class TicketUpdate(BaseModel):
    """Model for updating a ticket."""
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    status: Optional[TicketStatus] = None
    extracted_data: Optional[ExtractedData] = None


class MockEmailCreate(BaseModel):
    """Model for creating a mock email (development mode)."""
    from_email: EmailStr
    subject: Optional[str] = None
    body: str
    in_reply_to: Optional[int] = None  # ticket_id if replying
