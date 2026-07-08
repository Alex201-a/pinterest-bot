import base64
import json
import requests
from openai import OpenAI
from config import API_BASE_URL, API_KEY, MODEL


def get_client():
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def generate_text(theme: str, platform: str = "pinterest") -> dict:
    client = get_client()

    prompt = f"""Создай пост для {platform} на тему "{theme}".
Верни JSON:
{{
    "title": "заголовок (до 100 символов)",
    "description": "описание (до 500 символов)",
    "hashtags": ["тег1", "тег2", ...],
    "image_prompt": "промпт для генерации изображения на английском"
}}
Только JSON, без markdown."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def generate_image(prompt: str, output_path: str, size: str = "1024x1024") -> str:
    client = get_client()

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    img_data = requests.get(image_url).content

    with open(output_path, "wb") as f:
        f.write(img_data)

    return output_path


def generate_image_base64(prompt: str, size: str = "1024x1024") -> str:
    client = get_client()

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
        response_format="b64_json",
    )

    return response.data[0].b64_json


def generate_post(theme: str, platform: str = "pinterest") -> dict:
    text_data = generate_text(theme, platform)
    image_b64 = generate_image_base64(text_data["image_prompt"])

    return {
        "title": text_data["title"],
        "description": text_data["description"],
        "hashtags": text_data["hashtags"],
        "image_base64": image_b64,
    }
