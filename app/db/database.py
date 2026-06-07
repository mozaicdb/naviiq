from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_db():
    try:
        db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
        db_instance.db = db_instance.client[settings.DATABASE_NAME]
        await db_instance.client.admin.command("ping")
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise e

async def disconnect_db():
    try:
        if db_instance.client:
            db_instance.client.close()
            logger.info("MongoDB disconnected")
            print("MongoDB disconnected")
    except Exception as e:
        logger.error(f"MongoDB disconnect failed: {e}")
        raise e

def get_db():
    return db_instance.db

def get_collection(collection_name: str):
    return db_instance.db[collection_name]