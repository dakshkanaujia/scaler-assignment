import os
import httpx
import datetime
from dotenv import load_dotenv

load_dotenv()

async def check_availability():
    """Checks for available time slots in the next 7 days."""
    api_key = os.getenv("CALCOM_API_KEY")
    event_type_id = os.getenv("CALCOM_EVENT_TYPE_ID")
    
    if not api_key or not event_type_id:
        return "Cal.com API Key or Event Type ID not configured."

    today = datetime.datetime.now()
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = f"https://api.cal.com/v1/slots?apiKey={api_key}&eventTypeId={event_type_id}&dateFrom={date_from}&dateTo={date_to}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            slots = data.get("slots", {})
            available_slots = []
            
            for date, day_slots in slots.items():
                for slot in day_slots:
                    if len(available_slots) < 5:
                        available_slots.append(slot.get("time"))
                    else:
                        break
                if len(available_slots) >= 5:
                    break
            
            if not available_slots:
                return "No available slots found for the next 7 days."
            
            return "Available slots:\n" + "\n".join(available_slots)
            
    except Exception as e:
        return f"Error checking availability: {str(e)}"

async def book_slot(email: str, iso_time: str):
    """Books a meeting slot for a specific time."""
    api_key = os.getenv("CALCOM_API_KEY")
    event_type_id = os.getenv("CALCOM_EVENT_TYPE_ID")
    
    if not api_key or not event_type_id:
        return "Cal.com API Key or Event Type ID not configured."

    # Simple name extraction from email
    name = email.split("@")[0].capitalize()
    
    url = f"https://api.cal.com/v1/bookings?apiKey={api_key}"
    payload = {
        "eventTypeId": int(event_type_id),
        "start": iso_time,
        "responses": {
            "name": name,
            "email": email,
            "location": {"value": "integrations:google:meet", "optionValue": ""}
        },
        "timeZone": "UTC",
        "language": "en",
        "metadata": {}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            booking = data.get("booking", {})
            booking_id = booking.get("id")
            short_url = booking.get("shortUrl")
            
            return f"Booking confirmed! ID: {booking_id}. Meeting link: {short_url}"
            
    except Exception as e:
        return f"Error booking slot: {str(e)}"

# Gemini Function Declarations
TOOLS = [
    {
        "name": "check_availability",
        "description": "Check for available meeting slots in the next 7 days.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "book_slot",
        "description": "Book a meeting slot at a specific ISO 8601 time.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The email address of the person booking the meeting."
                },
                "iso_time": {
                    "type": "string",
                    "description": "The ISO 8601 formatted start time of the meeting (e.g., 2024-04-12T10:00:00Z)."
                }
            },
            "required": ["email", "iso_time"]
        }
    }
]
