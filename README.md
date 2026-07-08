# Pinterest & Instagram Content Bot

Автоматическая генерация и публикация контента через MiMo/OpenAI-совместимый API.

## Установка

```bash
pip install -r requirements.txt
cp .env.example .env
```

## Настройка

Заполните `.env`:

| Переменная | Описание |
|---|---|
| `API_BASE_URL` | URL MiMo/OpenAI API |
| `API_KEY` | Ваш API ключ |
| `MODEL` | Модель (gpt-4o, mimo и т.д.) |
| `PINTEREST_ACCESS_TOKEN` | Токен Pinterest |
| `PINTEREST_BOARD_ID` | ID доски Pinterest |
| `INSTAGRAM_ACCESS_TOKEN` | Токен Instagram Graph API |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | ID бизнес-аккаунта IG |

## Получение токенов

### Pinterest
1. Создайте приложение на https://developers.pinterest.com/
2. Получите access token через OAuth

### Instagram (Facebook Graph API)
1. Создайте приложение на https://developers.facebook.com/
2. Подключите Instagram Business-аккаунт
3. Получите токен с нужными разрешениями

## Использование

```bash
# Превью (без публикации)
python main.py preview

# Превью с конкретной темой
python main.py preview "healthy food"

# Одноразовая публикация
python main.py post

# Только Pinterest
python main.py post-pinterest "travel tips"

# Только Instagram
python main.py post-instagram "lifestyle"

# Автоматический планировщик
python main.py schedule
```

## Структура

```
├── config.py        — конфигурация из .env
├── generator.py     — генерация текста и изображений
├── pinterest.py     — публикация в Pinterest
├── instagram.py     — публикация в Instagram
├── main.py          — CLI и планировщик
└── .env.example     — шаблон переменных
```
