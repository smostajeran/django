import json
import re
from openai import OpenAI

client = OpenAI()

# ✅ Strong prompt: garment color only, ignore background
SYSTEM_PROMPT = """
You are a fashion item classifier.

CRITICAL COLOR RULE:
- You MUST output the dominant color of the CLOTHING ITEM ONLY.
- Ignore background (walls, floors, bedsheets), mannequins, skin tone, hangers, shadows, reflections, lighting casts.
- If multiple colors exist, choose the dominant fabric color.
- If background is highly dominant, still choose the clothing color, NOT the background.

Return ONLY valid JSON with these keys:
category, subcategory, color_primary, color_secondary, pattern, material, season.

Allowed categories:
top, bottom, outerwear, shoes, bag, watch, accessory, dress, skirt

Allowed pattern:
solid, striped, checked, printed, other

Allowed season:
all, summer, winter, spring, autumn

Color output format:
Use simple lowercase names like:
black, white, gray, navy, blue, light_blue, green, olive, beige, brown, tan,
red, burgundy, pink, purple, yellow, orange, metallic, multicolor.
"""


def _safe_extract_json(text: str) -> dict:
    """
    Extract JSON object even if model returns extra text.
    """
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"Model did not return JSON. Raw: {text}")
    return json.loads(match.group(0))


def _apply_guardrails(category: str, subcategory: str | None) -> tuple[str, str | None]:
    """
    Hard correction rules to prevent common mistakes.
    """
    if subcategory:
        s = subcategory.lower()

        # ✅ Jeans should NEVER become accessory
        if "jean" in s or "denim" in s:
            return "bottom", "Jeans"

        # ✅ Shorts always bottom
        if "short" in s:
            return "bottom", "Shorts"

        # ✅ Hoodie / sweatshirt should be top
        if "hoodie" in s or "sweatshirt" in s:
            return "top", subcategory

    return category, subcategory


def _normalize(data: dict) -> dict:
    """
    Normalize outputs to match our backend enums & defaults.
    """

    # defaults
    category = (data.get("category") or "accessory").strip().lower()
    subcategory = data.get("subcategory")

    color_primary = data.get("color_primary")
    color_secondary = data.get("color_secondary")

    pattern = (data.get("pattern") or "solid").strip().lower()
    material = data.get("material")
    season = (data.get("season") or "all").strip().lower()

    # allowed values (backend enums)
    allowed_categories = {"top", "bottom", "outerwear", "shoes", "bag", "watch", "accessory", "dress", "skirt"}
    allowed_patterns = {"solid", "striped", "checked", "printed", "other"}
    allowed_seasons = {"all", "summer", "winter", "spring", "autumn"}

    if category not in allowed_categories:
        category = "accessory"

    if pattern not in allowed_patterns:
        pattern = "solid"

    if season not in allowed_seasons:
        season = "all"

    # guardrails
    category, subcategory = _apply_guardrails(category, subcategory)

    # normalize color strings
    if isinstance(color_primary, str):
        color_primary = color_primary.strip().lower()

    if isinstance(color_secondary, str):
        color_secondary = color_secondary.strip().lower()

    return {
        "category": category,
        "subcategory": subcategory,
        "color_primary": color_primary,
        "color_secondary": color_secondary,
        "pattern": pattern,
        "material": material,
        "season": season,
    }


def _color_is_suspicious(subcategory: str | None, color_primary: str | None) -> bool:
    """
    Detect suspicious background colors (common failures).
    If model outputs background tones often, retry once.
    """
    if not color_primary:
        return True

    suspicious_backgrounds = {"white", "beige", "cream", "light_gray", "gray"}

    s = (subcategory or "").lower()

    # jeans/denim are rarely beige/white unless white jeans
    if "jean" in s or "denim" in s:
        return color_primary in {"white", "beige", "cream"}

    return color_primary in suspicious_backgrounds


def _run_model(image_url: str, prompt: str) -> tuple[dict, str]:
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Classify the fashion item and return STRICT JSON only. "
                            "Color MUST be the clothing fabric color (ignore background)."
                        ),
                    },
                    {"type": "input_image", "image_url": image_url},
                ],
            },
        ],
        max_output_tokens=220,
        temperature=0.0,
    )

    raw_text = response.output_text.strip()
    data = _safe_extract_json(raw_text)
    return data, raw_text


def detect_item_from_image_url(image_url: str) -> dict:
    """
    Returns:
    {
      "category": "bottom",
      "subcategory": "Jeans",
      "color_primary": "blue",
      "color_secondary": null,
      "pattern": "solid",
      "material": "denim",
      "season": "all",
      "raw_output": "...debug..."
    }
    """

    # First attempt
    try:
        data, raw_text = _run_model(image_url, SYSTEM_PROMPT)
        normalized = _normalize(data)
        normalized["raw_output"] = raw_text
    except Exception as e:
        return {
            "category": "accessory",
            "subcategory": None,
            "color_primary": None,
            "color_secondary": None,
            "pattern": "solid",
            "material": None,
            "season": "all",
            "raw_output": f"ERROR: {e}",
        }

    # ✅ Retry once if suspicious background-like color
    if _color_is_suspicious(normalized.get("subcategory"), normalized.get("color_primary")):
        retry_prompt = SYSTEM_PROMPT + "\n\nIMPORTANT: Previous color looked like background. Re-evaluate and output ONLY clothing fabric color."
        try:
            data2, raw_text2 = _run_model(image_url, retry_prompt)
            normalized2 = _normalize(data2)
            normalized2["raw_output"] = raw_text2
            return normalized2
        except Exception:
            pass

    return normalized
