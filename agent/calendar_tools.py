import os
import httpx
import datetime
from dotenv import load_dotenv

load_dotenv()

CAL_BASE = "https://api.cal.com/v2"
SLOTS_VERSION = "2024-09-04"
BOOKINGS_VERSION = "2024-08-13"


def _headers(version: str) -> dict:
    api_key = os.getenv("CALCOM_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "cal-api-version": version,
        "Content-Type": "application/json",
    }


async def check_availability():
    """Checks for available time slots in the next 7 days using Cal.com v2 API."""
    event_type_id = os.getenv("CALCOM_EVENT_TYPE_ID")

    if not os.getenv("CALCOM_API_KEY") or not event_type_id:
        return "Cal.com API Key or Event Type ID not configured."

    now = datetime.datetime.utcnow()
    start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    end = (now + datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = f"{CAL_BASE}/slots"
    params = {
        "eventTypeId": event_type_id,
        "start": start,
        "end": end,
        "timeZone": "UTC",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=_headers(SLOTS_VERSION))
            print(f"[check_availability] status={response.status_code} body={response.text[:500]}")
            response.raise_for_status()
            data = response.json()

            # v2 response: {"data": {"2026-04-13": [{"start": "..."}], ...}}
            slots_by_date = data.get("data", {})
            available_slots = []

            for date, day_slots in slots_by_date.items():
                for slot in day_slots:
                    if len(available_slots) < 5:
                        available_slots.append(slot.get("start"))
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
    """Books a meeting slot using Cal.com v2 API."""
    event_type_id = os.getenv("CALCOM_EVENT_TYPE_ID")

    if not os.getenv("CALCOM_API_KEY") or not event_type_id:
        return "Cal.com API Key or Event Type ID not configured."

    name = email.split("@")[0].replace(".", " ").replace("_", " ").title()

    url = f"{CAL_BASE}/bookings"
    payload = {
        "eventTypeId": int(event_type_id),
        "start": iso_time,
        "attendee": {
            "name": name,
            "email": email,
            "timeZone": "UTC",
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=_headers(BOOKINGS_VERSION))
            print(f"[book_slot] status={response.status_code} body={response.text[:500]}")
            response.raise_for_status()
            data = response.json()

            # v2 response: {"status":"success","data":{"uid":"...","title":"...","start":"..."}}
            booking = data.get("data", {})
            uid = booking.get("uid")
            title = booking.get("title", "Meeting")
            start = booking.get("start", iso_time)

            return f"Booking confirmed! '{title}' at {start}. Booking ID: {uid}"

    except httpx.HTTPStatusError as e:
        return f"Error booking slot: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error booking slot: {str(e)}"
