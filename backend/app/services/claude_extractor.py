"""
Claude API integration for extracting quote details from emails
and generating follow-up messages.
"""

import anthropic
import json
from typing import Dict, List
from app.config import settings
from app.models.ticket import ExtractedData


# Initialize Claude client
claude_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def extract_quote_details(email_body: str, email_subject: str = "") -> ExtractedData:
    """
    Extract quote request details from email using Claude API.

    Args:
        email_body: The email content
        email_subject: The email subject line

    Returns:
        ExtractedData object with extracted fields
    """

    prompt = f"""You are an AI assistant helping extract quote request details from customer emails.

Email Subject: {email_subject}

Email Content:
{email_body}

Extract the following fields as JSON. If a field is not mentioned, set it to null:
- customer_name: The customer's full name
- customer_email: The customer's email address
- laptop_model: Specific laptop model (brand and model number)
- ram: RAM size (e.g., "16GB", "32GB")
- storage: Storage size and type (e.g., "512GB SSD", "1TB HDD")
- screen_size: Screen size (e.g., "14-inch", "15.6-inch")
- warranty: Warranty details (e.g., "3-year ProSupport", "1 year")
- quantity: Number of laptops (e.g., "25 units", "10")
- delivery_location: Full delivery address or location
- delivery_timeline: When they need delivery (e.g., "March 15, 2026", "ASAP")
- budget: Their budget if mentioned (e.g., "$30,000", "around 50k")

Return ONLY valid JSON with these exact field names. Do not include any explanation or markdown formatting."""

    try:
        message = claude_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        extracted_dict = json.loads(response_text)

        # Create ExtractedData object
        return ExtractedData(**extracted_dict)

    except Exception as e:
        print(f"Error extracting data with Claude: {e}")
        # Return empty ExtractedData on error
        return ExtractedData()


def generate_followup_email(
    customer_name: str,
    missing_fields: List[str],
    extracted_data: ExtractedData
) -> Dict[str, str]:
    """
    Generate a follow-up email asking for missing information.

    Args:
        customer_name: Customer's name
        missing_fields: List of missing field names
        extracted_data: The partially extracted data

    Returns:
        Dict with "subject" and "body" keys
    """

    # Convert field names to human-readable format
    field_mapping = {
        "laptop_model": "laptop model and specifications",
        "ram": "RAM size",
        "storage": "storage capacity",
        "screen_size": "screen size",
        "warranty": "warranty requirements",
        "quantity": "quantity needed",
        "delivery_location": "delivery location",
        "delivery_timeline": "delivery timeline"
    }

    missing_readable = [field_mapping.get(f, f) for f in missing_fields]

    # Get what they DID provide for context
    provided_info = []
    for field, value in extracted_data.model_dump().items():
        if value and field not in missing_fields and field != "budget":
            readable_field = field_mapping.get(field, field)
            provided_info.append(f"{readable_field}: {value}")

    provided_context = "\n".join(provided_info) if provided_info else "your laptop quote request"

    prompt = f"""You are a professional sales assistant. Generate a friendly, concise follow-up email asking for missing information.

Customer name: {customer_name or "there"}

Information they already provided:
{provided_context}

Missing information needed:
{', '.join(missing_readable)}

Generate a professional email with:
1. A subject line (just the subject, no "Subject:" prefix)
2. The email body

The email should:
- Be warm and professional
- Thank them for their inquiry
- Mention what they already provided (briefly)
- Ask for the specific missing details in a clear list
- Keep it concise (under 150 words)

Return in this exact JSON format:
{{
    "subject": "subject line here",
    "body": "email body here"
}}

Return ONLY the JSON, no markdown formatting or explanations."""

    try:
        message = claude_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        email_dict = json.loads(response_text)

        return email_dict

    except Exception as e:
        print(f"Error generating follow-up with Claude: {e}")
        # Return a default follow-up on error
        return {
            "subject": "Additional Information Needed for Your Quote Request",
            "body": f"""Hello {customer_name or ""},

Thank you for your laptop quote request. To provide you with an accurate quote, I need a few more details:

{chr(10).join(f'- {field}' for field in missing_readable)}

Please reply to this email with the above information, and I'll get your quote to you promptly.

Best regards,
Sales Team"""
        }
