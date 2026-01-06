import os
import json
import re
import requests

# ✅ Your taxonomy
TAXONOMY = {
    "top": [
        "T-Shirts", "Shirts", "Blouses", "Polos", "Tank Tops",
        "Hoodies", "Sweatshirts", "Sweaters", "Cardigans"
    ],
    "bottom": [
        "Jeans", "Trousers", "Chinos", "Shorts",
        "Skirts", "Leggings", "Joggers"
    ],
    "outerwear": [
        "Jackets", "Coats", "Blazers", "Bomber Jackets",
        "Parkas", "Raincoats", "Vests"
    ],
    "dress_jumpsuit": [
        "Casual Dresses", "Evening Dresses", "Maxi Dresses",
        "Mini Dresses", "Party Dresses", "Jumpsuits", "Playsuits"
    ],
    "set": ["Matching Sets", "Tracksuits", "Lounge Sets", "Suit Sets"],
    "activewear": [
        "Sports Tops", "Sports Bras", "Gym Leggings",
        "Training Shorts", "Tracksuits", "Performance Jackets"
    ],
    "sleepwear": [
        "Pajama Sets", "Nightgowns", "Robes",
        "Lounge Pants", "Homewear Tops"
    ],
    "underwear_basics": [
        "Briefs / Boxers", "Bras", "Socks",
        "Undershirts", "Shapewear"
    ],
    "swimwear": [
        "Bikini Sets", "One-piece Swimsuits",
        "Swim Shorts", "Cover-Ups / Kaftans"
    ],
    "traditional": ["Abaya", "Kaftan", "Thobe / Kandura", "Kurta Sets"],
}


def _flatten_subcategories():
    subs = []
    for _, items in TAXONOMY.items():
        subs.extend(items)
    return subs


ALL_SUBCATEGORIES = _flatten_subcategories()


def _safe_extract_json(text: str) -> dict:
    """
    Extract JSON object from model text (even if extra text exists)
    """
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"Model did not return JSON. Raw: {text}")
    return json.loads(match.group(0))


def _apply_guardrails(category: str, subcategory: str) -> tuple[str, str]:
    """
    Hard correction rules to prevent common mistakes
    """
    if subcategory:
        s = subcategory.lower()

        # ✅ Jeans should NEVER become accessory
        if "jean" in s or "denim" in s:
            return "bottom", "Jeans"

        # ✅ Shorts always bottom
        if "short" in s:
            return "bottom", "Shorts"

    return category, subcategory


def detect_item_from_image_url(image_url: str) -> dict:
    """
    Returns:
    {
      "category": "bottom",
      "subcategory": "Jeans",
      "confidence": 0.92
    }
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not found in environment")

    taxonomy_json = json.dumps(TAXONOMY, indent=2)

    prompt = f"""
You are a clothing classifier.

You MUST classify the image into ONLY the taxonomy below.
Return STRICT JSON only.

Taxonomy:
{taxonomy_json}

Rules:
- Jeans MUST always be category "bottom" and subcategory "Jeans".
- Category must be one of: {list(TAXONOMY.keys())}
- Subcategory must be exactly one of the taxonomy subcategories
- confidence must be between 0 and 1
- If unsure, pick the closest valid match

Return JSON format:
{{
  "category": "...",
  "subcategory": "...",
  "confidence": 0.0
}}
"""

    payload = {
        "model": "gpt-4o-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
        "temperature": 0.0,
    }

    res = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if res.status_code != 200:
        raise Exception(f"OpenAI error {res.status_code}: {res.text}")

    data = res.json()
    raw_text = data["output"][0]["content"][0]["text"]

    result = _safe_extract_json(raw_text)

    category = result.get("category")
    subcategory = result.get("subcategory")
    confidence = float(result.get("confidence", 0.0))

    # ✅ Validate category/subcategory against taxonomy
    if category not in TAXONOMY:
        category = "top"
        confidence = 0.2

    if subcategory not in ALL_SUBCATEGORIES:
        subcategory = None
        confidence = 0.2

    # ✅ Guardrails
    category, subcategory = _apply_guardrails(category, subcategory)

    return {
        "category": category,
        "subcategory": subcategory,
        "confidence": confidence,
    }
