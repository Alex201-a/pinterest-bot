import base64
import tempfile
import requests
from config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID


API_URL = "https://graph.facebook.com/v18.0"


def upload_image(image_base64: str) -> str:
    img_data = base64.b64decode(image_base64)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(img_data)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        response = requests.post(
            f"{API_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media",
            files={"file": ("image.png", f, "image/png")},
            data={"access_token": INSTAGRAM_ACCESS_TOKEN},
        )

    response.raise_for_status()
    return response.json()["id"]


def publish_post(container_id: str) -> dict:
    response = requests.post(
        f"{API_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        },
    )
    response.raise_for_status()
    return response.json()


def create_container(image_url: str, caption: str) -> str:
    response = requests.post(
        f"{API_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        },
    )
    response.raise_for_status()
    return response.json()["id"]


def post_to_instagram(post_data: dict, image_url: str = None, image_base64: str = None) -> dict:
    hashtags = " ".join(f"#{tag}" for tag in post_data["hashtags"])
    caption = f"{post_data['title']}\n\n{post_data['description']}\n\n{hashtags}"

    if image_url:
        container_id = create_container(image_url, caption)
    elif image_base64:
        container_id = upload_image(image_base64)
    else:
        raise ValueError("Нужен image_url или image_base64")

    return publish_post(container_id)
