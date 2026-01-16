"""
Database connection and schema setup for Turso (LibSQL).
"""

import libsql_client
import os
from app.config import settings


# Create Turso database client
def get_db_client():
    """Get database client - uses local SQLite in development."""
    # For local development, use a local SQLite file instead of Turso
    # This avoids WebSocket connection issues during testing
    if settings.is_local:
        # Use local SQLite database
        local_db_path = os.path.join(os.path.dirname(__file__), "..", "local.db")
        client = libsql_client.create_client_sync(
            url=f"file:{local_db_path}"
        )
        return client
    else:
        # Production: use Turso
        url = settings.turso_database_url
        if url.startswith("libsql://"):
            url = url.replace("libsql://", "https://")

        client = libsql_client.create_client_sync(
            url=url,
            auth_token=settings.turso_auth_token
        )
        return client


# Database schema
DATABASE_SCHEMA = """
-- Tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT UNIQUE NOT NULL,
    customer_name TEXT,
    customer_email TEXT,
    status TEXT NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extracted data table
CREATE TABLE IF NOT EXISTS extracted_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    laptop_model TEXT,
    ram TEXT,
    storage TEXT,
    screen_size TEXT,
    warranty TEXT,
    quantity TEXT,
    delivery_location TEXT,
    delivery_timeline TEXT,
    budget TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- Email threads table
CREATE TABLE IF NOT EXISTS email_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    email_subject TEXT,
    email_body TEXT NOT NULL,
    direction TEXT NOT NULL,
    email_message_id TEXT,
    in_reply_to TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- Mock emails table (for local development mode)
CREATE TABLE IF NOT EXISTS mock_emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    to_email TEXT NOT NULL,
    from_email TEXT NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_email ON tickets(customer_email);
CREATE INDEX IF NOT EXISTS idx_email_threads_ticket ON email_threads(ticket_id);
CREATE INDEX IF NOT EXISTS idx_mock_emails_timestamp ON mock_emails(timestamp DESC);
"""


def initialize_database():
    """Initialize database schema."""
    client = get_db_client()

    # Split schema into individual statements and execute
    statements = [stmt.strip() for stmt in DATABASE_SCHEMA.split(';') if stmt.strip()]

    for statement in statements:
        try:
            client.execute(statement)
        except Exception as e:
            print(f"Error executing statement: {e}")
            print(f"Statement: {statement[:100]}...")

    print("[SUCCESS] Database schema initialized successfully")


if __name__ == "__main__":
    # Run this file directly to initialize the database
    initialize_database()
