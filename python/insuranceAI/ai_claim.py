import base64
import json
import re
from openai import OpenAI
from flask import current_app

from models import CLAIM_CATEGORIES

SYSTEM_PROMPT = (
    "You are an assistant for an insurance company that drafts a short, "
    "structured claim summary from the information a policyholder submits. "
    "Read the claimant's details, their description of the incident, and any "
    "attached image or medical report, then produce a concise summary with "
    "these sections: Claimant Profile, Incident Summary, Medical Findings "
    "(if any), and Suggested Claim Category.\n\n"
    "For the Suggested Claim Category, select the most appropriate option from "
    "the following list, copied exactly as written:\n"
    + "\n".join(f"- {c}" for c in CLAIM_CATEGORIES) + "\n\n"
    "Keep the summary under 200 words. This is a classroom demo, not real "
    "medical or legal advice."
)


def _encode_image(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{data}"


def _split_medical_report(medical_report_path):
    """A medical report upload is either a .txt file (read as text) or an
    image (passed to the vision model as-is). Returns (text, image_path).
    """
    if not medical_report_path:
        return None, None
    if medical_report_path.lower().endswith(".txt"):
        with open(medical_report_path, "r", errors="ignore") as f:
            return f.read(), None
    return None, medical_report_path


def _fallback_summary(age, location, gender, description, medical_text):
    lines = [
        "[Offline demo summary - AI unavailable, showing a basic auto-generated summary instead]",
        f"Claimant Profile: {age}-year-old {gender}, located in {location}.",
        f"Incident Summary: {description.strip()}",
    ]
    if medical_text:
        lines.append(f"Medical Findings: {medical_text.strip()[:300]}")
    lines.append("Suggested Claim Category: General / Needs manual review.")
    return "\n".join(lines)


def generate_claim_summary(age, location, gender, description, image_path=None, medical_report_path=None):
    medical_text, medical_image_path = _split_medical_report(medical_report_path)

    api_key = current_app.config["GROQ_API_KEY"]
    if not api_key:
        return _fallback_summary(age, location, gender, description, medical_text)

    try:
        client = OpenAI(api_key=api_key, base_url=current_app.config["GROQ_BASE_URL"])

        content = [
            {
                "type": "text",
                "text": (
                    f"Age: {age}\nLocation: {location}\nGender: {gender}\n"
                    f"Claim description: {description}\n"
                    + (f"Medical report text: {medical_text}\n" if medical_text else "")
                ),
            }
        ]
        if image_path:
            content.append({"type": "image_url", "image_url": {"url": _encode_image(image_path)}})
        if medical_image_path:
            content.append({"type": "image_url", "image_url": {"url": _encode_image(medical_image_path)}})

        response = client.chat.completions.create(
            model=current_app.config["GROQ_MODEL"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            # The default model is a reasoning model whose reasoning depth
            # varies a lot by input -- it can burn anywhere from 500 to well
            # over 1500 tokens thinking before it writes a single word of the
            # actual summary. max_tokens has to cover both worst cases, or
            # the response gets cut off mid-thought with empty content
            # (finish_reason "length", zero-length message.content).
            max_tokens=3000,
            # Without this, the response also includes a <think>...</think>
            # block instead of just the summary.
            extra_body={"reasoning_format": "hidden"},
        )
        summary = response.choices[0].message.content
        if not summary:
            # Reasoning ate the entire token budget and left nothing for the
            # actual answer (finish_reason "length") -- no exception was
            # raised, so this has to be checked explicitly or it'd silently
            # return an empty summary instead of falling back.
            raise RuntimeError(
                f"Groq returned an empty response (finish_reason={response.choices[0].finish_reason})"
            )
        return summary
    except Exception as exc:
        return (
            _fallback_summary(age, location, gender, description, medical_text)
            + f"\n\n(AI call failed: {exc})"
        )


ADVISOR_SYSTEM_PROMPT = (
    "You help a policyholder use a claim submission web form. Read the incident "
    "description and any medical report they give you, then:\n"
    "1. Pick exactly ONE category from this fixed list: "
    + ", ".join(f'"{c}"' for c in CLAIM_CATEGORIES) + "\n"
    "2. Give a 1-2 sentence reason for that category.\n"
    "3. Give a short ordered checklist (4-6 steps) telling them exactly what to do on "
    "the 'New Claim' form of this app, which has these fields: Age, Location, Gender, "
    "Claim description (textarea), an optional incident photo upload, and an optional "
    "medical report upload. Steps should reference filling in THESE fields, not general "
    "real-world insurance advice (e.g. do not tell them to call the police or contact "
    "an adjuster).\n"
    'Respond with ONLY a JSON object shaped like: {"category": "<one of the list above, '
    'exactly>", "reason": "<1-2 sentences>", "steps": ["<step 1>", "<step 2>", ...]}. '
    "This is a classroom demo, not real insurance advice."
)


_STOPWORDS = {"or", "and", "the", "a", "an", "of", "etc"}


def _normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _significant_words(text):
    return set(_normalize(text).split()) - _STOPWORDS


def _match_category(raw_category):
    """The model is told to copy a category exactly, but reasoning models
    sometimes paraphrase it slightly (different punctuation/case/word order,
    e.g. "Personal Injury or Accident" instead of "Personal Injury / Accident")
    even when its own reasoning clearly points at the right one. A strict
    `raw_category in CLAIM_CATEGORIES` check would silently throw that away
    and fall back to "Other / Not Sure" -- this matches more forgivingly
    before giving up.
    """
    if not raw_category:
        return "Other / Not Sure"
    normalized_raw = _normalize(raw_category)

    for c in CLAIM_CATEGORIES:
        if _normalize(c) == normalized_raw:
            return c
    for c in CLAIM_CATEGORIES:
        normalized_c = _normalize(c)
        if normalized_c in normalized_raw or normalized_raw in normalized_c:
            return c

    # Last resort: every significant word of a candidate category shows up
    # somewhere in the raw text, regardless of order or filler words.
    raw_words = _significant_words(raw_category)
    for c in CLAIM_CATEGORIES:
        c_words = _significant_words(c)
        if c_words and c_words.issubset(raw_words):
            return c

    return "Other / Not Sure"


def _fallback_suggestion(error=None):
    return {
        "category": "Other / Not Sure",
        "reason": "AI suggestion unavailable right now - review the description yourself and pick the closest category.",
        "steps": [
            "Re-read your description and note the type of loss: vehicle, injury, property, or illness.",
            "Pick the closest matching category in the New Claim form.",
            "Fill in your age, location, and gender.",
            "Paste or write your claim description.",
            "Attach a photo of the incident/item if you have one.",
            "Attach your medical report if applicable.",
            "Review everything and submit.",
        ],
        "error": error,
    }


def suggest_claim_category(description, medical_report_path=None):
    """Advisory call made BEFORE a claim is submitted: given a plain-language
    description (and optionally a medical report file), ask the AI which
    category to pick and what to do on the New Claim form. Returns a dict:
    {"category": str, "reason": str, "steps": list[str], "error": str|None}.
    """
    medical_text, medical_image_path = _split_medical_report(medical_report_path)

    api_key = current_app.config["GROQ_API_KEY"]
    if not api_key:
        return _fallback_suggestion()

    try:
        client = OpenAI(api_key=api_key, base_url=current_app.config["GROQ_BASE_URL"])

        content = [
            {
                "type": "text",
                "text": (
                    f"What happened: {description}\n"
                    + (f"Medical report text: {medical_text}\n" if medical_text else "")
                ),
            }
        ]
        if medical_image_path:
            content.append({"type": "image_url", "image_url": {"url": _encode_image(medical_image_path)}})

        response = client.chat.completions.create(
            model=current_app.config["GROQ_MODEL"],
            messages=[
                {"role": "system", "content": ADVISOR_SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            # JSON mode on this reasoning model can burn well over 1000
            # tokens thinking before it writes the actual JSON -- too low a
            # budget here fails with "max tokens reached before generating
            # a valid document" instead of a normal empty-content response.
            max_tokens=3000,
            extra_body={"reasoning_format": "hidden"},
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        category = _match_category(data.get("category"))
        return {
            "category": category,
            "reason": data.get("reason", ""),
            "steps": data.get("steps") or [],
            "error": None,
        }
    except Exception as exc:
        return _fallback_suggestion(error=str(exc))
