from motor.motor_asyncio import AsyncIOMotorClient
from src.core.settings.configurations.config import settings
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pymongo.errors import PyMongoError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection parameters
MONGO_DB_URL = settings.MONGO_DB_URL
MONGO_DB_NAME = settings.MONGO_DB_NAME

# Retry configuration for establishing the MongoDB connection
@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    reraise=True  # Raise the last exception if all retries fail
)
def create_mongo_client():
    try:
        client = AsyncIOMotorClient(
            MONGO_DB_URL,
            maxPoolSize=100,  # Maximum number of connections in the pool
            minPoolSize=10,   # Minimum number of connections in the pool
            serverSelectionTimeoutMS=5000,  # Timeout for server selection
            tls=True,  # Enable TLS/SSL for secure connection
            tlsAllowInvalidCertificates=False  # Disallow invalid certificates
        )
        logger.info("Successfully connected to MongoDB.")
        return client
    except PyMongoError as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

# Initialize MongoDB Client
client = create_mongo_client()
db_client = client[MONGO_DB_NAME]

# Collections Access
template_collection = db_client["templates"]




