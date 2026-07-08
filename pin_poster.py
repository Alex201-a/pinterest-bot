import os
import sys
import json
import time
import base64
import random
import string
import requests
from datetime import datetime, timezone, timedelta

KIEV_TZ = timezone(timedelta(hours=3))

PINS_DIR = os.environ.get("PINS_DIR", "pins_data")
DESCRIPTIONS_FILE = os.path.join(PINS_DIR, "описание.txt")
POSTED_LOG = os.path.join(PINS_DIR, "posted.txt")
ETSY_LINKS_FILE = os.path.join(os.path.dirname(__file__), "etsy_links.json")

PINTEREST_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN")
PINTEREST_BOARD = os.environ.get("PINTEREST_BOARD_ID")


def log(msg):
    now = datetime.now(KIEV_TZ)
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')} КИЕВ] {msg}")


def load_descriptions():
    pins = {}
    current_pin = None
    current_section = None
    title = ""
    description = ""

    with open(DESCRIPTIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if line.endswith(".jpeg") and line.split(".")[0].isdigit():
                if current_pin is not None:
                    pins[current_pin] = {"title": title, "description": description}
                current_pin = int(line.split(".")[0])
                current_section = None
                title = ""
                description = ""
            elif line == "Title:":
                current_section = "title"
            elif line == "Description:":
                current_section = "description"
            elif current_section == "title" and line:
                title = line
            elif current_section == "description" and line:
                description = line

        if current_pin is not None:
            pins[current_pin] = {"title": title, "description": description}

    return pins


def load_etsy_links():
    with open(ETSY_LINKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_etsy_url(title, description, etsy_links):
    content = (title + " " + description).lower()

    if "pregnant" in content or "pumpkin mama" in content or "growing little pumpkin" in content:
        return etsy_links.get("pregnant", "")

    if "hippo" in content:
        if "vampire" in content or "dracula" in content:
            return etsy_links.get("hippo_vampire", "")
        elif "witch" in content:
            return etsy_links.get("hippo_witch", "")
        elif "skeleton" in content:
            return etsy_links.get("hippo_skeleton", "")
        elif "mummy" in content:
            return etsy_links.get("hippo_mummy", "")
        elif "ghost" in content:
            return etsy_links.get("hippo_ghost", "")
        return etsy_links.get("hippo_vampire", "")

    if "raccoon" in content or "trash panda" in content:
        if "lantern" in content or "jack" in content:
            return etsy_links.get("raccoon_lantern", "")
        elif "skeleton" in content:
            return etsy_links.get("raccoon_skeleton", "")
        elif "bat" in content:
            return etsy_links.get("raccoon_bat", "")
        elif "spider" in content:
            return etsy_links.get("raccoon_spider", "")
        elif "candy" in content:
            return etsy_links.get("raccoon_candy", "")
        elif "ghost" in content:
            return etsy_links.get("raccoon_ghost", "")
        elif "witch" in content:
            return etsy_links.get("raccoon_witch", "")
        return etsy_links.get("raccoon_skeleton", "")

    if "dachshund" in content or "dog" in content:
        return etsy_links.get("dachshund_ghost", "")

    if "capybara" in content:
        if "bat" in content or "wing" in content:
            return etsy_links.get("capybara_bat", "")
        elif "witch" in content:
            return etsy_links.get("capybara_witch", "")
        elif "spider" in content:
            return etsy_links.get("capybara_spider", "")
        elif "lantern" in content or "jack" in content:
            return etsy_links.get("capybara_lantern", "")
        return etsy_links.get("capybara_bat", "")

    return etsy_links.get("pregnant", "")


def get_utm_link(etsy_url, pin_num):
    if not etsy_url:
        return ""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{etsy_url}?utm_source=pinterest&utm_medium=pin&utm_campaign=pin_{pin_num}_{suffix}"


def get_hashtags(title, description):
    content = (title + " " + description).lower()
    tags = ["halloween", "digitalart"]

    if "hippo" in content:
        tags.append("hippo")
    elif "raccoon" in content:
        tags.append("raccoon")
    elif "capybara" in content:
        tags.append("capybara")
    elif "dachshund" in content:
        tags.append("dachshund")
    elif "pumpkin" in content:
        tags.append("pumpkin")
    else:
        tags.append("spookyseason")

    tags.append("printable")
    return tags[:5]


def post_to_pinterest(title, description, image_path, link):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    hashtags = get_hashtags(title, description)
    hashtag_str = " ".join(f"#{t}" for t in hashtags)

    full_desc = f"{title}\n\n{description}\n\n{hashtag_str}"

    payload = {
        "title": title,
        "description": full_desc,
        "board_id": PINTEREST_BOARD,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": img_b64,
        },
    }

    if link:
        payload["link"] = link

    headers = {
        "Authorization": f"Bearer {PINTEREST_TOKEN}",
        "Content-Type": "application/json",
    }

    resp = requests.post("https://api.pinterest.com/v5/pins", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_posted():
    posted = set()
    if os.path.exists(POSTED_LOG):
        with open(POSTED_LOG, "r") as f:
            for line in f:
                posted.add(int(line.strip()))
    return posted


def mark_posted(num):
    with open(POSTED_LOG, "a") as f:
        f.write(f"{num}\n")


def get_next_pin():
    descriptions = load_descriptions()
    posted = get_posted()

    for num in sorted(descriptions.keys()):
        if num not in posted:
            return num, descriptions[num]
    return None, None


def post_one():
    if not PINTEREST_TOKEN:
        log("ОШИБКА: PINTEREST_ACCESS_TOKEN не задан")
        return False

    if not PINTEREST_BOARD:
        log("ОШИБКА: PINTEREST_BOARD_ID не задан")
        return False

    etsy_links = load_etsy_links()
    pin_num, pin_data = get_next_pin()

    if pin_num is None:
        log("Все пины опубликованы!")
        return False

    image_path = os.path.join(PINS_DIR, f"{pin_num}.jpeg")
    if not os.path.exists(image_path):
        log(f"Нет файла: {pin_num}.jpeg")
        return False

    etsy_url = get_etsy_url(pin_data["title"], pin_data["description"], etsy_links)
    link = get_utm_link(etsy_url, pin_num)

    log(f"ПИН #{pin_num}: {pin_data['title']}")
    log(f"Ссылка: {link}")

    try:
        result = post_to_pinterest(pin_data["title"], pin_data["description"], image_path, link)
        log(f"PINTEREST: OK! ID: {result.get('id', 'ok')}")
        mark_posted(pin_num)
        return True
    except Exception as e:
        log(f"ОШИБКА: {e}")
        return False


def show_status():
    descriptions = load_descriptions()
    posted = get_posted()
    total = len(descriptions)
    done = len(posted)
    remaining = total - done
    days = remaining / 15 if remaining > 0 else 0

    log(f"Всего: {total}")
    log(f"Опубликовано: {done}")
    log(f"Осталось: {remaining}")
    log(f"Дней: {days:.1f}")


def main():
    if len(sys.argv) < 2:
        print("python pin_poster.py post       — один пин сейчас")
        print("python pin_poster.py scheduled  — пин с задержкой ±10 мин")
        print("python pin_poster.py status     — статус")
        return

    cmd = sys.argv[1]
    if cmd == "post":
        post_one()
    elif cmd == "status":
        show_status()
    elif cmd == "scheduled":
        delay = random.randint(60, 600)
        log(f"Задержка: {delay} сек ({delay//60} мин {delay%60} сек)")
        time.sleep(delay)
        post_one()


if __name__ == "__main__":
    main()
