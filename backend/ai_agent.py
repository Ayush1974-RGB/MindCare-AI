import re
from typing import Iterator

try:
    from .tools import call_emergency, query_medgemma, stream_medgemma
except ImportError:
    from tools import call_emergency, query_medgemma, stream_medgemma


EMERGENCY_PATTERNS = (
    r"\bi (?:am|'m) (?:going to|about to|planning to) (?:kill|hurt) myself\b",
    r"\bi (?:want|intend|plan) to (?:kill myself|end my life|die by suicide)\b",
    r"\bi (?:have|made) a (?:suicide )?plan\b",
    r"\bi (?:just|already) (?:cut myself|overdosed|took (?:the |a )?(?:pills|poison))\b",
    r"\bi (?:have|am holding) (?:a )?(?:gun|knife|weapon) .{0,30}\bmyself\b",
    r"\bi(?:'m| am) attempting suicide\b",
)

NEGATED_EMERGENCY_PATTERNS = (
    r"\bi (?:do not|don't|dont) want to (?:kill|hurt) myself\b",
    r"\bi (?:am|'m) not (?:suicidal|going to hurt myself)\b",
    r"\bi (?:have|had) no (?:plan|intention) to (?:kill|hurt) myself\b",
    r"\bi would never (?:kill|hurt) myself\b",
)


def requires_emergency_call(message: str) -> bool:
    """Return True only for explicit, immediate first-person danger."""
    normalized = " ".join(message.lower().split())

    if any(re.search(pattern, normalized) for pattern in NEGATED_EMERGENCY_PATTERNS):
        return False

    return any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS)


def get_nearby_therapists(message: str) -> str | None:
    normalized = message.lower()
    therapist_terms = ("nearby therapist", "therapist near me", "find a therapist")
    if not any(term in normalized for term in therapist_terms):
        return None

    return (
        "I can help you look for professional support. Please share your city or area, "
        "or use a trusted local healthcare directory to find a licensed therapist nearby."
    )


def get_simple_greeting(message: str) -> str | None:
    normalized = " ".join(message.lower().split())
    if normalized not in {"hi", "hii", "hello", "hey", "heyy", "hey there"}:
        return None

    return (
        "Hi, I'm here with you. We can keep this simple: tell me how your day has "
        "felt, what is bothering you, or one word for your current mood. What would "
        "you like to start with?"
    )


def handle_message(message: str, history: list[dict] | None = None) -> tuple[str, str]:
    """
    Route a message without using a second model as a tool selector.

    Emergency calling is deliberately restricted to explicit, immediate danger.
    All ordinary conversation goes directly to the local MedGemma model.
    """
    if requires_emergency_call(message):
        try:
            call_emergency()
            call_status = "emergency_call_tool"
            call_note = "An emergency call has been requested."
        except Exception:
            call_status = "emergency_call_unavailable"
            call_note = (
                "Automated calling is not configured, so please call local emergency "
                "services now."
            )

        return (
            "I’m really concerned that you may be in immediate danger. Please move away "
            "from anything you could use to hurt yourself and contact local emergency "
            f"services or a trusted person who can stay with you right now. {call_note}",
            call_status,
        )

    therapist_response = get_nearby_therapists(message)
    if therapist_response:
        return therapist_response, "find_nearby_therapists"

    greeting_response = get_simple_greeting(message)
    if greeting_response:
        return greeting_response, "supportive_greeting"

    return query_medgemma(message, history), "ask_mental_health_specialist"


def stream_message(message: str, history: list[dict] | None = None) -> Iterator[str]:
    """Stream normal replies while keeping safety handling deterministic."""
    if requires_emergency_call(message):
        response, _ = handle_message(message)
        yield response
        return

    greeting_response = get_simple_greeting(message)
    if greeting_response:
        yield greeting_response
        return

    yield from stream_medgemma(message, history)
