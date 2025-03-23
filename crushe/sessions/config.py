from os import getenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_ID = int(getenv("API_ID", "25276967"))
API_HASH = getenv("API_HASH", "daf793293a5a244e5c426a129656e0a1")
BOT_TOKEN = getenv("BOT_TOKEN", "7204564003:AAEZ59EzGa7yXhrdLgTuse7lyIUt5oFL55g")
OWNER_ID = list(map(int, filter(None, getenv("OWNER_ID", "922270982").split())))
MONGO_DB = getenv("MONGO_DB", "mongodb+srv://yairhmirsnda417gillette:p60u615i6lxQLVwx@cluster0.sdxo5.mongodb.net/?retryWrites=true&w=majority")
LOG_GROUP = int(getenv("LOG_GROUP", "-1002493565037"))
CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002329264016"))
FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "20"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "500"))
WEBSITE_URL = getenv("WEBSITE_URL", "")
AD_API = getenv("AD_API", "")
STRING = getenv("STRING", "")
YT_COOKIES = getenv("YT_COOKIES", "")
INSTA_COOKIES = getenv("INSTA_COOKIES", "")
SECONDS = 300  # for example, a 5-minute delay