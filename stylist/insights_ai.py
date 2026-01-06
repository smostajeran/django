import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a professional personal stylist.
You will receive:
- user's inventory summary (counts by category/subcategory/colors)
- user's taste summary from likes/dislikes (liked categories/colors vs disliked)
- user's profile preferences (preferred/disliked colors/styles)

You must return ONLY JSON with:
{
  "buy": [
    {"item_type": "...", "reason": "...", "confidence": 0.0-1.0}
  ],
  "dont_buy": [
    {"item_type": "...", "reason": "...", "confidence": 0.0-1.0}
  ]
}

Rules:
- Suggestions must be practical and specific.
- "dont_buy" should include duplicates or items that conflict with taste.
- "buy" should focus on missing essentials, versatile pieces that match taste, and items that will improve outfit variety.
- If the user has very few wardrobe items, recommend basic essentials first.
- Keep each reason under 30 words.
Return 5 to 8 items in each list.
"""


def generate_buy_dont_buy(profile_context, inventory_summary, taste_summary):
    payload = {
        "profile": profile_context,
        "inventory_summary": inventory_summary,
        "taste_summary": taste_summary,
    }

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        max_output_tokens=600,
    )

    text = response.output_text.strip()
    return json.loads(text)
