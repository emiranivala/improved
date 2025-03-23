#crushe
import asyncio
import logging
import time
from pyromod import listen
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.get_event_loop()
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

async def create_client(name, **kwargs):
    max_retries = 5  # Increased max retries
    base_delay = 3   # Base delay for exponential backoff
    max_delay = 60   # Maximum delay between retries
    
    for attempt in range(max_retries):
        try:
            client = Client(name, **kwargs)
            await client.start()
            
            # Set up disconnect handler
            @client.on_disconnect
            async def handle_disconnect():
                logging.warning(f"Client {name} disconnected. Attempting to reconnect...")
                try:
                    await client.start()
                    logging.info(f"Client {name} reconnected successfully")
                except Exception as e:
                    logging.error(f"Failed to reconnect client {name}: {str(e)}")
                    await asyncio.sleep(5)  # Add delay before retry
            
            # Set up keep-alive mechanism with connection lock
            connection_lock = asyncio.Lock()
            async def keep_alive():
                while True:
                    try:
                        async with connection_lock:
                            if not client.is_connected:
                                await client.start()
                        await asyncio.sleep(300)  # Check every 5 minutes
                    except Exception as e:
                        logging.warning(f"Keep-alive check failed for {name}: {str(e)}")
                        await asyncio.sleep(60)
            
            asyncio.create_task(keep_alive())
            logging.info(f"Successfully connected client: {name}")
            return client
            
        except Exception as e:
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (2 ** attempt), max_delay)
                logging.warning(f"Client {name} connection attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logging.error(f"Failed to connect client {name} after {max_retries} attempts: {str(e)}")
                raise

botStartTime = time.time()

# Initialize clients as None
app = None
pro = None
sex = None

# Client configurations
app_config = {
    "name": ":RestrictBot:",
    "api_id": API_ID,
    "api_hash": API_HASH,
    "bot_token": BOT_TOKEN,
    "workers": 10
}

pro_config = {
    "name": "ggbot",
    "api_id": API_ID,
    "api_hash": API_HASH,
    "session_string": STRING
}


# MongoDB setup with retry logic
async def get_mongo_client():
    max_retries = 5
    base_delay = 3  # Base delay for exponential backoff
    max_delay = 60  # Maximum delay between retries
    
    for attempt in range(max_retries):
        try:
            client = AsyncIOMotorClient(
                MONGO_DB,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
                maxPoolSize=10,  # Reduced pool size to prevent connection overload
                minPoolSize=1,   # Ensure at least one connection is maintained
                maxIdleTimeMS=30000,  # Close idle connections after 30 seconds
                retryWrites=True,
                w=1  # Write concern for better consistency
            )
            # Verify connection is alive
            await client.admin.command('ping')
            
            # Set up reconnection handler with connection cleanup
            async def monitor_connection():
                while True:
                    try:
                        await client.admin.command('ping')
                        await asyncio.sleep(60)  # Check every minute
                    except Exception as e:
                        logging.warning(f"MongoDB connection lost: {str(e)}. Attempting to reconnect...")
                        try:
                            # Ensure proper cleanup of existing connections
                            client.close()
                            await asyncio.sleep(1)  # Wait for connections to close
                            # Attempt to reconnect with a new client instance
                            await client.admin.command('ping')
                            logging.info("MongoDB reconnected successfully")
                        except Exception as e:
                            logging.error(f"MongoDB reconnection failed: {str(e)}")
                            await asyncio.sleep(5)
                    finally:
                        # Ensure we don't have too many idle connections
                        client.get_io_loop().create_task(client.close_cursor_tasks())
            
            asyncio.create_task(monitor_connection())
            logging.info("Successfully connected to MongoDB")
            return client
            
        except Exception as e:
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                logging.warning(f"MongoDB connection attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logging.error(f"Failed to connect to MongoDB after {max_retries} attempts: {str(e)}")
                raise

tclient = None
tdb = None
token = None

async def setup_mongo():
    global tclient, tdb, token
    tclient = await get_mongo_client()
    tdb = tclient["telegram_bot"]  # Your database
    token = tdb["tokens"]  # Your tokens collection

async def create_ttl_index():
    """Ensure the TTL index exists for the `tokens` collection."""
    await token.create_index("expires_at", expireAfterSeconds=0)

# Run the TTL index creation when the bot starts
async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

# You can call this in your main bot file before starting the bot

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME, app, pro, sex, tclient, tdb, token
    
    # Setup MongoDB first
    await setup_mongo()
    await setup_database()
    
    # Initialize main bot client
    try:
        app = await create_client(**app_config)
        getme = await app.get_me()
        BOT_ID = getme.id
        BOT_USERNAME = getme.username
        BOT_NAME = getme.first_name + (" " + getme.last_name if getme.last_name else "")
        logging.info(f"Bot initialized as {BOT_NAME} (@{BOT_USERNAME})")
        
        # Initialize pro client if STRING is provided
        if STRING:
            pro = await create_client(**pro_config)
            logging.info("Pro client initialized successfully")
            
        # Initialize Telethon client with enhanced error handling
        sex = TelegramClient('sexrepo', API_ID, API_HASH,
                           device_model="Telethon Bot",
                           system_version="1.0",
                           app_version="1.0",
                           flood_sleep_threshold=60)

        # Set up reconnection handler
        @sex.on(events.disconnected)
        async def handle_disconnection(event):
            logging.warning("Telethon client disconnected. Attempting to reconnect...")
            try:
                await sex.connect()
                if not await sex.is_user_authorized():
                    await sex.start(bot_token=BOT_TOKEN)
                logging.info("Telethon client reconnected successfully")
            except Exception as e:
                logging.error(f"Failed to reconnect Telethon client: {str(e)}")

        await sex.start(bot_token=BOT_TOKEN)
        logging.info("Telethon client initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize clients: {str(e)}")
        raise

async def main():
    try:
        await restrict_bot()
        logging.info("Bot started successfully")
    except Exception as e:
        logging.error(f"Failed to start bot: {str(e)}")
        raise

loop.run_until_complete(main())
