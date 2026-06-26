import math
from functools import lru_cache
from typing import Iterator

import ollama
import requests
from twilio.rest import Client

try:
    from .config import (
        EMERGENCY_CONTACT,
        OLLAMA_MODEL,
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_FROM_NUMBER,
    )
except ImportError:
    from config import (
        EMERGENCY_CONTACT,
        OLLAMA_MODEL,
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_FROM_NUMBER,
    )


MODEL_NAME = OLLAMA_MODEL
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Multiple Overpass mirrors tried in order if one times out or fails
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
OVERPASS_URL = OVERPASS_MIRRORS[0]  # kept for backward compat
LOCATION_HEADERS = {
    "User-Agent": "MindHarborApp/1.0 (noida-mentalhealth-dashboard; contact@mindharbor.org)",
    "Accept": "application/json,text/plain,*/*",
}

BROAD_LOCATION_FALLBACKS = {
    "haryana": [
        "Gurugram, Haryana, India",
        "Faridabad, Haryana, India",
        "Panchkula, Haryana, India",
    ],
    "delhi": ["New Delhi, India", "South Delhi, India", "Rohini, Delhi, India"],
    "india": ["New Delhi, India", "Mumbai, India", "Bengaluru, India"],
}

STATIC_GEOCODES = {
    "haryana": {
        "lat": 29.0588,
        "lon": 76.0856,
        "display_name": "Haryana, India",
    },
    "gurugram": {
        "lat": 28.4595,
        "lon": 77.0266,
        "display_name": "Gurugram, Haryana, India",
    },
    "gurgaon": {
        "lat": 28.4595,
        "lon": 77.0266,
        "display_name": "Gurugram, Haryana, India",
    },
    "faridabad": {
        "lat": 28.4089,
        "lon": 77.3178,
        "display_name": "Faridabad, Haryana, India",
    },
    "panchkula": {
        "lat": 30.6942,
        "lon": 76.8606,
        "display_name": "Panchkula, Haryana, India",
    },
    "gurugram, haryana, india": {
        "lat": 28.4595,
        "lon": 77.0266,
        "display_name": "Gurugram, Haryana, India",
    },
    "faridabad, haryana, india": {
        "lat": 28.4089,
        "lon": 77.3178,
        "display_name": "Faridabad, Haryana, India",
    },
    "panchkula, haryana, india": {
        "lat": 30.6942,
        "lon": 76.8606,
        "display_name": "Panchkula, Haryana, India",
    },
    "new delhi, india": {
        "lat": 28.6139,
        "lon": 77.2090,
        "display_name": "New Delhi, India",
    },
    "noida": {
        "lat": 28.5706,
        "lon": 77.3272,
        "display_name": "Noida, Uttar Pradesh, India",
    },
    "noida, uttar pradesh, india": {
        "lat": 28.5706,
        "lon": 77.3272,
        "display_name": "Noida, Uttar Pradesh, India",
    },
}

THERAPIST_SYSTEM_PROMPT = """
You are MindHarbor, a warm mental-health support companion, not a doctor.
Reply in 80-120 words: naturally acknowledge the feeling, offer one or two practical
next steps, then ask one gentle relevant question. Use clear everyday language and
short paragraphs. Never diagnose or prescribe. For immediate danger, encourage local
emergency help and staying with a trusted person.
If the user asks for a quote, motivation, general wellness information, or a practical
tool, answer that request directly. Do not assume anxiety, overwhelm, or poor sleep
unless the user actually mentions it.
""".strip()


def fallback_support_response(prompt: str) -> str:
    """Return a useful response when the local model is unavailable."""
    lower_prompt = prompt.lower()
    if any(word in lower_prompt for word in ("hi", "hii", "hello", "hey")) and len(lower_prompt.split()) <= 4:
        return (
            "Hi, I'm here with you. We can keep this very simple: you can tell me what "
            "kind of day it has been, what is bothering you, or just one word for how "
            "you feel right now. What would you like to start with?"
        )
    if any(word in lower_prompt for word in ("panic", "anxious", "anxiety", "overwhelmed")):
        return (
            "I hear that this feels intense right now. Try one slow breath in for four "
            "counts, hold for two, and breathe out for six. Then choose one tiny next "
            "step for the next five minutes. What is the strongest feeling in your body "
            "right now?"
        )
    if any(word in lower_prompt for word in ("sleep", "tired", "insomnia")):
        return (
            "That racing-mind feeling can be exhausting. Keep the next step simple: dim "
            "the screen, loosen your shoulders, and write one sentence about what your "
            "mind is trying to solve. What usually starts the loop when you try to rest?"
        )
    if any(word in lower_prompt for word in ("sad", "low", "depressed", "lonely")):
        return (
            "I'm sorry today feels heavy. You do not have to solve the whole feeling at "
            "once. Try one caring action: water, food, a short walk, or messaging one safe "
            "person. What has made the day feel hardest?"
        )
    if any(word in lower_prompt for word in ("angry", "frustrated", "irritated", "mad")):
        return (
            "That sounds really frustrating. Before reacting, give yourself a little room: "
            "name what crossed the line, then choose one action that protects your peace "
            "without making things worse. What happened right before the feeling spiked?"
        )
    if any(word in lower_prompt for word in ("relationship", "friend", "family", "partner", "breakup")):
        return (
            "Relationships can feel heavy when something important is unclear or unmet. "
            "Try separating the facts from the story your mind is building around them. "
            "What do you most wish the other person understood?"
        )
    if any(word in lower_prompt for word in ("work", "exam", "study", "school", "college", "deadline")):
        return (
            "That kind of pressure can make everything feel urgent at once. Pick the "
            "smallest visible task, set a ten-minute timer, and let that be enough for "
            "now. What is the one task that would reduce the most stress if started?"
        )
    return (
        "I'm here with you. It may help to slow the moment down: what happened, what did "
        "you feel, and what would make the next ten minutes a little easier? Start with "
        "one sentence, and we can sort it out together."
    )


def _model_messages(prompt: str, history: list[dict] | None = None) -> list[dict]:
    messages = [{"role": "system", "content": THERAPIST_SYSTEM_PROMPT}]
    for item in (history or [])[-8:]:
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": prompt})
    return messages


def stream_medgemma(prompt: str, history: list[dict] | None = None) -> Iterator[str]:
    """Stream a concise supportive response from the local model."""
    try:
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=_model_messages(prompt, history),
            stream=True,
            options={
                "num_predict": 500,
                "num_ctx": 4096,
                "temperature": 0.75,
                "top_p": 0.88,
                "repeat_penalty": 1.10,
            },
            keep_alive="30m",
        )
        produced_text = False
        for chunk in stream:
            text = chunk.get("message", {}).get("content", "")
            if text:
                produced_text = True
                yield text

        if not produced_text:
            yield "I couldn't form a response just now. Please try once more."
    except Exception:
        yield fallback_support_response(prompt)


def query_medgemma(prompt: str, history: list[dict] | None = None) -> str:
    return "".join(stream_medgemma(prompt, history)).strip()


def call_emergency() -> str:
    required_values = (
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_FROM_NUMBER,
        EMERGENCY_CONTACT,
    )
    if not all(required_values):
        raise RuntimeError("Twilio emergency calling is not configured.")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=EMERGENCY_CONTACT,
        from_=TWILIO_FROM_NUMBER,
        url="http://demo.twilio.com/docs/voice.xml",
    )
    return call.sid


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


@lru_cache(maxsize=64)
def geocode_location(location: str) -> dict:
    """Geocode a location string to coordinates. Raises ValueError if not found."""
    normalized = " ".join(location.lower().split())
    if normalized in STATIC_GEOCODES:
        return STATIC_GEOCODES[normalized]

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": location, "format": "jsonv2", "limit": 1, "accept-language": "en"},
            headers=LOCATION_HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError(
                f"Could not find location '{location}'. "
                "Try a different spelling, a nearby city, or a postal code."
            )

        result = results[0]
        return {
            "lat": float(result["lat"]),
            "lon": float(result["lon"]),
            "display_name": result["display_name"],
        }
    except requests.Timeout:
        raise ValueError(
            "The location lookup timed out. Please check your internet connection and try again."
        )
    except requests.ConnectionError:
        raise ValueError(
            "Cannot connect to the location service. Please check your internet connection."
        )
    except requests.HTTPError as e:
        if response.status_code == 429:
            raise ValueError(
                "Too many location lookups. Please wait a moment and try a different search."
            )
        raise ValueError(f"Location service error: {response.status_code}. Please try again.")


def _care_query(lat: float, lon: float, radius_m: int) -> str:
    """Build a lean Overpass QL query with a 25-second timeout budget."""
    return f"""
[out:json][timeout:25];
(
  nwr(around:{radius_m},{lat},{lon})["healthcare"~"psychotherapist|psychologist|counsellor|psychiatrist"];
  nwr(around:{radius_m},{lat},{lon})["healthcare:speciality"~"psychiatry|psychotherapy|clinical_psychology|counselling|mental_health"];
  nwr(around:{radius_m},{lat},{lon})["office"~"therapist|counsellor|counselor"];
  nwr(around:{radius_m},{lat},{lon})["amenity"~"clinic|hospital|doctors"]["name"~"mental|psychi|psycholog|counsel|therapy|mind",i];
);
out center tags;
"""


def _parse_care_elements(elements: list[dict], center: dict) -> list[dict]:
    facilities = []
    seen = set()
    lat, lon = center["lat"], center["lon"]

    for element in elements:
        tags = element.get("tags", {})
        item_lat = element.get("lat") or element.get("center", {}).get("lat")
        item_lon = element.get("lon") or element.get("center", {}).get("lon")
        if item_lat is None or item_lon is None:
            continue

        name = tags.get("name") or tags.get("operator") or "Mental health support"
        phone = tags.get("contact:phone") or tags.get("phone")
        website = tags.get("contact:website") or tags.get("website")
        speciality = (
            tags.get("healthcare:speciality")
            or tags.get("healthcare")
            or tags.get("office")
            or tags.get("amenity")
            or "mental health care"
        )
        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city"),
        ]
        address = " ".join(part for part in address_parts if part)
        key = (name.lower(), round(float(item_lat), 4), round(float(item_lon), 4))
        if key in seen:
            continue
        seen.add(key)

        facilities.append(
            {
                "name": name,
                "phone": phone,
                "website": website,
                "speciality": speciality.replace("_", " ").replace(";", ", "),
                "address": address or "Address not available in OpenStreetMap",
                "lat": float(item_lat),
                "lon": float(item_lon),
                "distance_km": round(
                    _distance_km(lat, lon, float(item_lat), float(item_lon)), 1
                ),
            }
        )

    facilities.sort(key=lambda item: item["distance_km"])
    return facilities


def _search_care_near(place: dict, radius_km: int) -> list[dict]:
    """Query Overpass mirrors in sequence; return parsed results on first success."""
    radius_m = max(2, min(radius_km, 25)) * 1000
    lat, lon = place["lat"], place["lon"]
    query = _care_query(lat, lon, radius_m)
    last_error = "All map servers are currently unavailable."

    for mirror in OVERPASS_MIRRORS:
        try:
            response = requests.post(
                mirror,
                data={"data": query},
                headers=LOCATION_HEADERS,
                timeout=30,
            )
            response.raise_for_status()
        except requests.Timeout:
            last_error = "The healthcare database lookup timed out. Trying another server..."
            continue
        except requests.ConnectionError:
            last_error = "Cannot connect to the healthcare database. Trying another server..."
            continue
        except requests.HTTPError:
            last_error = "The healthcare database returned an error. Trying another server..."
            continue

        try:
            payload = response.json()
        except Exception:
            last_error = "Received an unreadable response from the map server."
            continue

        # Overpass signals timeout inside the JSON body as a "remark"
        remark = payload.get("remark", "")
        if "timed out" in remark or "runtime error" in remark:
            last_error = "The map server timed out processing this area. Trying another server..."
            continue

        elements = payload.get("elements", [])
        return _parse_care_elements(elements, place)

    raise ValueError(last_error)


@lru_cache(maxsize=64)
def find_nearby_care(location: str, radius_km: int = 12) -> dict:
    """Find nearby mental-health-related facilities from OpenStreetMap."""
    requested_location = location.strip()
    place = geocode_location(requested_location)
    service_errors = []
    try:
        facilities = _search_care_near(place, radius_km)
    except ValueError as exc:
        facilities = []
        service_errors.append(str(exc))
    searched_places = [place["display_name"]]
    fallback_note = None

    normalized = requested_location.lower().strip()
    fallback_locations = BROAD_LOCATION_FALLBACKS.get(normalized, [])
    if not facilities and fallback_locations:
        fallback_note = (
            f"'{requested_location}' is a broad location, so I also checked larger city "
            "centers where OpenStreetMap is more likely to have specialist listings."
        )
        merged = []
        seen = set()
        for fallback_location in fallback_locations:
            fallback_place = geocode_location(fallback_location)
            searched_places.append(fallback_place["display_name"])
            try:
                fallback_items = _search_care_near(fallback_place, 25)
            except ValueError as exc:
                service_errors.append(str(exc))
                fallback_items = []
            for item in fallback_items:
                key = (item["name"].lower(), round(item["lat"], 4), round(item["lon"], 4))
                if key not in seen:
                    seen.add(key)
                    merged.append(item)
        facilities = merged

    if not facilities:
        if service_errors:
            fallback_note = (
                "The map provider is not returning specialist listings right now. Try a "
                "more specific city or postal code, and verify providers directly through "
                "a trusted healthcare directory or hospital referral."
            )
        else:
            fallback_note = (
                "No specialist listings were found in OpenStreetMap for this search. Try a "
                "more specific city, neighborhood, or postal code, such as 'Gurugram, Haryana'."
            )

    return {
        "location": place["display_name"],
        "center": {"lat": place["lat"], "lon": place["lon"]},
        "results": facilities[:12],
        "message": fallback_note,
        "searched_places": searched_places,
        "service_errors": service_errors,
        "source": "OpenStreetMap contributors",
    }
