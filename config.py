# devgagan
# Note if you are trying to deploy on vps then directly fill values in ("")

from os import getenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")
OWNER_ID = list(map(int, filter(None, getenv("OWNER_ID", "").split())))
MONGO_DB = getenv("MONGO_DB", "mongodb+srv://crushe:crushe123@cluster0.rlmxpqw.mongodb.net/?retryWrites=true&w=majority")
LOG_GROUP = getenv("LOG_GROUP", "")
CHANNEL_ID = int(getenv("CHANNEL_ID", "0"))
FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "20"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "500"))
WEBSITE_URL = getenv("WEBSITE_URL")
AD_API = getenv("AD_API")
STRING = getenv("STRING")
YT_COOKIES = getenv("YT_COOKIES")
INSTA_COOKIES = getenv("INSTA_COOKIES")
SECONDS = 300  # for example, a 5-minute delay
