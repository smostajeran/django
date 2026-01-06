import requests
from io import BytesIO
from PIL import Image
from rembg import remove


def remove_background_from_url(image_url: str) -> bytes:
    """
    Downloads an image from URL, removes background, returns PNG bytes.
    """
    r = requests.get(image_url, timeout=30)
    r.raise_for_status()

    input_image = Image.open(BytesIO(r.content)).convert("RGBA")

    # remove bg
    output_image = remove(input_image)

    buf = BytesIO()
    output_image.save(buf, format="PNG")
    return buf.getvalue()
