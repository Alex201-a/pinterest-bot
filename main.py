import sys
import json
import random
import schedule
import time
from datetime import datetime

from config import CONTENT_THEME, POSTS_PER_DAY
from generator import generate_post
from pinterest import post_to_pinterest
from instagram import post_to_instagram


def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def run_once(platform: str = "both", theme: str = None):
    if theme is None:
        themes = [t.strip() for t in CONTENT_THEME.split(",")]
        theme = random.choice(themes)

    log(f"Генерация поста: тема='{theme}', платформа={platform}")

    try:
        if platform in ("pinterest", "both"):
            log("Генерация для Pinterest...")
            post = generate_post(theme, "pinterest")
            result = post_to_pinterest(post)
            log(f"Pinterest: опубликовано! ID: {result.get('id', 'ok')}")

        if platform in ("instagram", "both"):
            log("Генерация для Instagram...")
            post = generate_post(theme, "instagram")
            result = post_to_instagram(post, image_base64=post["image_base64"])
            log(f"Instagram: опубликовано! ID: {result.get('id', 'ok')}")

    except Exception as e:
        log(f"ОШИБКА: {e}")


def run_scheduler():
    themes = [t.strip() for t in CONTENT_THEME.split(",")]
    interval_hours = 24 / POSTS_PER_DAY

    log(f"Запуск планировщика: {POSTS_PER_DAY} постов/день, интервал {interval_hours:.1f}ч")

    for i in range(POSTS_PER_DAY):
        hour = int(8 + i * interval_hours)
        time_str = f"{hour:02d}:00"
        schedule.every().day.at(time_str).do(run_once, platform="both", theme=random.choice(themes))
        log(f"Запланировано: {time_str}")

    while True:
        schedule.run_pending()
        time.sleep(60)


def preview(theme: str = None):
    if theme is None:
        themes = [t.strip() for t in CONTENT_THEME.split(",")]
        theme = random.choice(themes)

    log(f"Превью: тема='{theme}'")
    from generator import generate_text

    for platform in ("pinterest", "instagram"):
        data = generate_text(theme, platform)
        print(f"\n{'='*50}")
        print(f"Платформа: {platform.upper()}")
        print(f"Заголовок: {data['title']}")
        print(f"Описание: {data['description']}")
        print(f"Хэштеги: {', '.join('#'+t for t in data['hashtags'])}")
        print(f"Промпт: {data['image_prompt']}")


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python main.py preview [тема]     — превью контента")
        print("  python main.py post [тема]        — одноразовая публикация")
        print("  python main.py schedule           — запуск планировщика")
        print("  python main.py post-pinterest [тема]  — только Pinterest")
        print("  python main.py post-instagram [тема]  — только Instagram")
        return

    cmd = sys.argv[1]
    theme = sys.argv[2] if len(sys.argv) > 2 else None

    if cmd == "preview":
        preview(theme)
    elif cmd == "post":
        run_once("both", theme)
    elif cmd == "post-pinterest":
        run_once("pinterest", theme)
    elif cmd == "post-instagram":
        run_once("instagram", theme)
    elif cmd == "schedule":
        run_scheduler()
    else:
        print(f"Неизвестная команда: {cmd}")


if __name__ == "__main__":
    main()
