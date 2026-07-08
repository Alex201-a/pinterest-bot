import base64
import requests
from config import PINTEREST_ACCESS_TOKEN, PINTEREST_BOARD_ID


API_URL = "https://api.pinterest.com/v5"


def create_pin(title: str, description: str, image_base64: str, link: str = "") -> dict:
    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    hashtags = " ".join(f"#{tag}" for tag in description.get("hashtags", []))
    full_description = f"{description['text']}\n\n{hashtags}" if isinstance(description, dict) else description

    payload = {
        "title": title,
        "description": full_description,
        "board_id": PINTEREST_BOARD_ID,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/png",
            "data": image_base64,
        },
    }

    if link:
        payload["link"] = link

    response = requests.post(f"{API_URL}/pins", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def post_to_pinterest(post_data: dict) -> dict:
    description = {
        "text": post_data["description"],
        "hashtags": post_data["hashtags"],
    }

    return create_pin(
        title=post_data["title"],
        description=description,
        image_base64=post_data["image_base64"],
    )
