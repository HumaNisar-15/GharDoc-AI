"""Gemini integration: send photos, receive JSON, retry and fall back between models.

Errors are raised as AIUnavailable(code). The app translates the code with i18n key "err_<code>",
so users always see a clear message in their own language.
"""
import io
import json
import os
import re
import time

from PIL import Image, ImageOps

import config

ISSUE_TYPES = ["dampness", "hairline_crack", "structural_crack", "plaster_peeling",
               "pipe_leak", "no_visible_issue", "unclear"]
WORKERS = ["plumber", "mason", "painter", "engineer"]
CHANGES = ["bigger", "same", "smaller", "unclear"]
ERROR_CODES = ["no_key", "bad_key", "busy", "parse"]

LANG_RULE = {
    "roman": ("Write ALL text fields in Roman Urdu: Urdu written with English letters, simple everyday words, "
              "short sentences (example: 'Ye deewar par seelan lagti hai'). Do NOT use Urdu/Arabic script."),
    "en": "Write ALL text fields in simple, short English that an ordinary homeowner can understand.",
    "ur": ("Write ALL text fields in Urdu using proper Urdu script (example: 'یہ دیوار پر سیلن لگتی ہے'). "
           "Use simple everyday words and short sentences. Keep technical terms such as DPC or epoxy accurate."),
}


class AIUnavailable(Exception):
    """The AI could not be reached or understood. `code` maps to an i18n message."""

    def __init__(self, code, detail=""):
        super().__init__(code if not detail else "%s: %s" % (code, detail))
        self.code = code if code in ERROR_CODES else "busy"
        self.detail = detail


def prepare_image(file_like):
    """Fix rotation, convert to RGB, downsize and return JPEG bytes."""
    img = Image.open(file_like)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((config.MAX_IMAGE_PX, config.MAX_IMAGE_PX))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def make_thumb(data, px=240):
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((px, px))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    return buf.getvalue()


def get_api_key():
    """Read the key from the environment or Streamlit secrets. It is never sent to the browser."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def is_configured():
    return bool(get_api_key())


def parse_json(text):
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        data = json.loads(t)
    except Exception:
        a, b = t.find("{"), t.rfind("}")
        if a == -1 or b <= a:
            raise ValueError("AI response was not JSON")
        data = json.loads(t[a:b + 1])
    if isinstance(data, list):  # the model sometimes wraps the object in a list
        data = next((x for x in data if isinstance(x, dict)), {})
    if not isinstance(data, dict):
        raise ValueError("AI response was not JSON")
    return data


def _client(key):
    from google import genai
    return genai.Client(api_key=key)


def _call(parts):
    """Try each configured model in order. Returns (text, model_name)."""
    key = get_api_key()
    if not key:
        raise AIUnavailable("no_key")
    from google.genai import types
    client = _client(key)
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
    last = None
    for model in config.MODELS:
        for attempt in range(config.RETRIES_PER_MODEL):
            try:
                resp = client.models.generate_content(model=model, contents=parts, config=cfg)
                if resp.text:
                    return resp.text, model
                last = RuntimeError("empty response")
            except Exception as e:  # noqa: BLE001
                last = e
                msg = str(e)
                if "API key not valid" in msg or "API_KEY_INVALID" in msg or "PERMISSION_DENIED" in msg:
                    raise AIUnavailable("bad_key") from e
                if "NOT_FOUND" in msg or "404" in msg:
                    break  # this model does not exist, try the next one
                time.sleep(config.RETRY_WAIT_SEC * (attempt + 1))
    raise AIUnavailable("busy", str(last)[:120])


def _image_parts(images):
    from google.genai import types
    return [types.Part.from_bytes(data=b, mime_type="image/jpeg") for b in images]


DIAG_PROMPT = """You are a cautious home-repair assistant for houses in Pakistan.
Look at the wall photo(s) and the owner's note. Reply ONLY with one single JSON object (not a list):
{
 "is_wall_photo": true or false,
 "issue_type": one of __ISSUES__,
 "probable_causes": [up to 3 short phrases],
 "confidence": number from 0 to 1,
 "risk_level": "green" or "yellow" or "red",
 "reason": "2-3 simple sentences for an ordinary person",
 "worker_type": one of __WORKERS__,
 "work_ids": [IDs chosen ONLY from the list below, can be empty],
 "questions": [3 to 5 questions the owner should ask the worker to avoid being overcharged],
 "recommended_fixes": [2 to 4 short practical steps, in order],
 "diy_ok": true only if the problem is purely cosmetic and safe for the owner to fix alone, otherwise false,
 "need_more_photos": true or false,
 "flags": {
   "near_structural_element": crack or damage near a column, beam or roof edge,
   "stair_step_or_diagonal": crack runs diagonal or in a stair-step pattern,
   "wide_or_widening": crack looks wide or is reported to be growing,
   "recurring_or_spreading": damp or damage is spreading or keeps coming back
 }
}
__LANG__
Keep JSON keys and the enum values above in English exactly as written.
Be cautious: if unsure choose the higher risk and set need_more_photos to true. Never invent prices.
Never say a building is safe. If the photo is not a wall or building surface, set is_wall_photo to false.
Allowed work IDs:
__WORKS__
Owner's note: __NOTE__"""

TRACK_PROMPT = """You compare two photos of the SAME wall crack. The first photo is the OLDER one
(date: __OLD__), the second is the NEWER one (date: __NEW__). Reply ONLY with one JSON object:
{
 "change": one of __CHANGES__,
 "explanation": "2 simple sentences about what you see",
 "advice": "1-2 simple sentences"
}
__LANG__
Keep JSON keys and the "change" value in English exactly as written.
Be cautious. If the photos are taken from different angles or distances and you cannot be sure, use "unclear"."""


def _num(x, default=0.0):
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return default


def _lst(d, k, n):
    v = d.get(k) or []
    return [str(x) for x in v][:n] if isinstance(v, list) else []


def normalize_diagnosis(d, valid_ids):
    flags_in = d.get("flags") if isinstance(d.get("flags"), dict) else {}
    issue = d.get("issue_type") if d.get("issue_type") in ISSUE_TYPES else "unclear"
    risk = d.get("risk_level") if d.get("risk_level") in ("green", "yellow", "red") else "yellow"
    worker = d.get("worker_type") if d.get("worker_type") in WORKERS else "engineer"
    ids = [w for w in (d.get("work_ids") or []) if w in valid_ids]
    return {
        "is_wall_photo": bool(d.get("is_wall_photo", True)),
        "issue_type": issue,
        "probable_causes": _lst(d, "probable_causes", 3),
        "confidence": _num(d.get("confidence")),
        "risk_level": risk,
        "reason": str(d.get("reason") or ""),
        "worker_type": worker,
        "work_ids": ids,
        "questions": _lst(d, "questions", 5),
        "recommended_fixes": _lst(d, "recommended_fixes", 4),
        "diy_ok": bool(d.get("diy_ok", False)),
        "need_more_photos": bool(d.get("need_more_photos", False)),
        "flags": {k: bool(flags_in.get(k, False)) for k in
                  ("near_structural_element", "stair_step_or_diagonal",
                   "wide_or_widening", "recurring_or_spreading")},
    }


def diagnose(images, note, rates_df, lang="en"):
    """images: list of prepare_image() bytes. Returns (normalized dict, model name)."""
    valid_ids = set(rates_df["id"].tolist())
    works = "\n".join("%s: %s" % (r.id, r.kaam) for r in rates_df.itertuples()) or "(none)"
    prompt = (DIAG_PROMPT.replace("__ISSUES__", str(ISSUE_TYPES)).replace("__WORKERS__", str(WORKERS))
              .replace("__LANG__", LANG_RULE.get(lang, LANG_RULE["en"])).replace("__WORKS__", works)
              .replace("__NOTE__", (note or "none").strip()[:500]))
    text, model = _call(_image_parts(images) + [prompt])
    try:
        data = parse_json(text)
    except ValueError as e:
        raise AIUnavailable("parse") from e
    return normalize_diagnosis(data, valid_ids), model


def track(old_img, new_img, old_date, new_date, lang="en"):
    prompt = (TRACK_PROMPT.replace("__OLD__", str(old_date)).replace("__NEW__", str(new_date))
              .replace("__CHANGES__", str(CHANGES)).replace("__LANG__", LANG_RULE.get(lang, LANG_RULE["en"])))
    text, model = _call(_image_parts([old_img, new_img]) + [prompt])
    try:
        d = parse_json(text)
    except ValueError as e:
        raise AIUnavailable("parse") from e
    change = d.get("change") if d.get("change") in CHANGES else "unclear"
    return {"change": change, "explanation": str(d.get("explanation") or ""),
            "advice": str(d.get("advice") or "").strip()}, model
