import os

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    API_BASE_URL = "https://www.rbstream.fun/api/search"
