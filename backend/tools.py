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
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
LOCATION_HEADERS = {
    "User-Agent": "MindHarbor-MentalHealth-Dashboard/1.0 (local educational project)"
}

THERAPIST_SYSTEM_PROMPT = """
You are MindHarbor, a warm mental-health support companion, not a doctor.
Reply in 50-100 words: naturally acknowledge the feeling, offer one or two practical
next steps, then ask one gentle relevant question. Use clear everyday language and
short paragraphs. Never diagnose or prescribe. For immediate danger, encourage local
emergency help and staying with a trusted person.
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
                "num_predict": 110,
                "num_ctx": 2048,
                "temperature": 0.72,
                "top_p": 0.85,
                "repeat_penalty": 1.12,
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
    response = requests.get(
        NOMINATIM_URL,
        params={"q": location, "format": "jsonv2", "limit": 1},
        headers=LOCATION_HEADERS,
        timeout=12,
    )
    response.raise_for_status()
    results = response.json()
    if not results:
        raise ValueError("Location not found.")

    result = results[0]
    return {
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
        "display_name": result["display_name"],
    }


@lru_cache(maxsize=64)
def find_nearby_care(location: str, radius_km: int = 12) -> dict:
    """Find nearby mental-health-related facilities from OpenStreetMap."""
    place = geocode_location(location.strip())
    radius_m = max(2, min(radius_km, 25)) * 1000
    lat, lon = place["lat"], place["lon"]

    query = f"""
    [out:json][timeout:25];
    (
      nwr(around:{radius_m},{lat},{lon})["healthcare"~"psychotherapist|psychologist|counsellor|psychiatrist"];
      nwr(around:{radius_m},{lat},{lon})["healthcare:speciality"~"psychiatry|psychotherapy|clinical_psychology|counselling"];
      nwr(around:{radius_m},{lat},{lon})["office"~"therapist|counsellor"];
    );
    out center tags;
    """
    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=LOCATION_HEADERS,
        timeout=35,
    )
    response.raise_for_status()

    facilities = []
    seen = set()
    for element in response.json().get("elements", []):
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
                "address": address,
                "lat": float(item_lat),
                "lon": float(item_lon),
                "distance_km": round(
                    _distance_km(lat, lon, float(item_lat), float(item_lon)), 1
                ),
            }
        )

    facilities.sort(key=lambda item: item["distance_km"])
    return {
        "location": place["display_name"],
        "center": {"lat": lat, "lon": lon},
        "results": facilities[:12],
        "source": "OpenStreetMap contributors",
    }
