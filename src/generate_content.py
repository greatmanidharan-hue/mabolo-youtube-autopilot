from __future__ import annotations

import json
import os
import random
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPICS_FILE = ROOT / "content" / "topics.json"
OUTPUT_DIR = ROOT / "output"


def load_topics() -> list[dict[str, Any]]:
    return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))


def _source_metadata(topic: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_urls": list(topic.get("source_urls") or []),
        "source_note": topic.get(
            "source_note",
            "Research leads only; verify each claim against the original publication."
        ),
        "sources_verified": False,
        "claim_checks": []
    }


def build_offline_draft(topic: dict[str, Any]) -> dict[str, object]:
    title = topic["topic"]
    angle = topic["angle"]
    draft = {
        "title": title,
        "format": "YouTube Short",
        "language": "Tamil",
        "topic": title,
        "research_angle": angle,
        "script": (
            f"வணக்கம்! இன்று நாம் பார்க்கப் போவது: {title}.\n\n"
            f"இந்தக் காணொளியில் கவனிக்க வேண்டிய முக்கிய கோணம்: {angle}.\n\n"
            "முதலில் கிடைக்கும் ஆதாரங்களைப் பார்ப்போம். அடுத்ததாக ஆய்வாளர்கள் "
            "கூறும் விளக்கங்களைப் புரிந்துகொள்வோம். கடைசியாக இன்னும் உறுதி "
            "செய்யப்படாத தகவல்களையும் தெளிவாகப் பிரித்துப் பார்ப்போம்.\n\n"
            "வரலாற்றை ஆதாரத்துடன் அறிந்துகொள்வோம். மேலும் இதுபோன்ற "
            "தமிழ் வரலாற்றுக் காணொளிகளுக்கு சேனலைப் பின்தொடருங்கள்!"
        ),
        "description": (
            f"{title}\n\n"
            "இந்தக் காணொளி கல்வி மற்றும் வரலாற்று ஆர்வத்திற்காக உருவாக்கப்படும் "
            "தொடக்க வரைவு. வெளியிடுவதற்கு முன் நம்பகமான தொல்லியல்/ஆய்வு "
            "ஆதாரங்களைச் சரிபார்க்கவும்."
        ),
        "hashtags": ["#தமிழ்வரலாறு", "#TamilHistory", "#TamilShorts"],
        "research_checklist": [
            "ஆதாரமான தொல்லியல் அல்லது கல்வி நிறுவன வெளியீடுகளைத் தேடவும்",
            "இலக்கிய மரபையும் தொல்லியல் சான்றையும் தனித்தனியாகக் குறிப்பிடவும்",
            "தேதி, இடம், நிபுணர் பெயர்களை வெளியீட்டுக்கு முன் சரிபார்க்கவும்"
        ],
        "generated_with": "offline-template",
        "review_required": True
    }
    draft.update(_source_metadata(topic))
    return draft


def generate_with_openrouter(topic: dict[str, Any], api_key: str, model: str) -> dict[str, object]:
    source_urls = topic.get("source_urls") or []
    prompt = (
        "Write a concise, original Tamil YouTube Shorts draft (about 45-60 seconds) "
        "on the supplied topic. Return ONLY valid JSON with keys: title, script, "
        "description, hashtags (array), research_checklist (array). "
        "Do not invent facts, dates, quotations or archaeological findings. "
        "Clearly mark disputed or uncertain claims and request source verification. "
        "Avoid copying any source text. The URLs supplied below are research leads only: "
        "do not imply you opened or read them, do not invent citations, and do not claim "
        "they prove any statement. Ask the human editor to verify every factual claim "
        "against the original publication.\n"
        f"Topic: {topic['topic']}\nAngle: {topic['angle']}\n"
        f"Research lead URLs: {json.dumps(source_urls, ensure_ascii=False)}"
    )
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/greatmanidharan-hue/mabolo-youtube-autopilot",
            "X-Title": "MABOLO YouTube Autopilot"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"AI provider request failed: {exc}") from exc

    content = payload["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    draft = json.loads(content)
    draft.update({
        "topic": topic["topic"],
        "language": "Tamil",
        "format": "YouTube Short",
        "generated_with": model,
        "review_required": True
    })
    draft.update(_source_metadata(topic))
    return draft


def main() -> Path:
    topics = load_topics()
    topic = random.choice(topics)
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    draft = (
        generate_with_openrouter(topic, api_key, model)
        if api_key else build_offline_draft(topic)
    )
    draft["created_at"] = datetime.now(timezone.utc).isoformat()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = OUTPUT_DIR / f"tamil-draft-{stamp}.json"
    path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Draft created: {path.relative_to(ROOT)}")
    print(f"Topic: {draft['topic']}")
    print(f"Provider: {draft['generated_with']}")
    return path


if __name__ == "__main__":
    main()
