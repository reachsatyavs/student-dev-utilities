import base64
from openai import OpenAI
from flask import current_app

SYSTEM_PROMPT = (
    "You are an assistant for an insurance company that drafts a short, "
    "structured claim summary from the information a policyholder submits. "
    "Read the claimant's details, their description of the incident, and any "
    "attached image or medical report, then produce a concise summary with "
    "these sections: Claimant Profile, Incident Summary, Medical Findings "
    "(if any), and Suggested Claim Category. Keep it under 200 words. This "
    "is a classroom demo, not real medical or legal advice."
)


def _encode_image(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{data}"


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
    medical_text = None
    medical_image_path = None
    if medical_report_path:
        if medical_report_path.lower().endswith(".txt"):
            with open(medical_report_path, "r", errors="ignore") as f:
                medical_text = f.read()
        else:
            medical_image_path = medical_report_path

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
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as exc:
        return (
            _fallback_summary(age, location, gender, description, medical_text)
            + f"\n\n(AI call failed: {exc})"
        )
