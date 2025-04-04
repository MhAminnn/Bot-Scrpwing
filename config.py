import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN", "8102146048:AAHqZOUNzwbmSauR6v81AWmPj29TuFH4s9E")

# API Configuration
ITZPIRE_API_URL = os.environ.get("ITZPIRE_API_URL", "https://itzpire.com/download/instagram")
FACEBOOK_API_URL = os.environ.get("FACEBOOK_API_URL", "https://api.ryzendesu.vip/api/downloader/fbdl") 
TIKTOK_API_URL = os.environ.get("TIKTOK_API_URL", "https://api.ryzendesu.vip/api/downloader/ttdl")
YOUTUBE_API_URL = os.environ.get("YOUTUBE_API_URL", "https://api.ryzendesu.vip/api/downloader/ytmp3")

# Media Configuration
MAX_MEDIA_PER_GROUP = int(os.environ.get("MAX_MEDIA_PER_GROUP", "10"))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))

# Bot Settings
DAILY_LIMIT = int(os.environ.get("DAILY_LIMIT", "10"))

# Debug Configuration
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
