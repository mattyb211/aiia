# backend/app/database.py
"""
Loads environment variables from backend/.env and sets up
Motor client for MongoDB with proper TLS/SSL configuration.
"""
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env in backend root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is missing – set it in backend/.env"
    )

# Determine database name
# Prefer explicit MONGO_DB_NAME env var, else parse URI path
db_name = os.getenv("MONGO_DB_NAME")
if not db_name:
    # parse the path segment from URI
    parsed = urlparse(MONGO_URI)
    path = parsed.path.lstrip("/")
    if path:
        db_name = path
    else:
        raise RuntimeError(
            "Database name not found. Please add MONGO_DB_NAME to your .env or include it in MONGO_URI path"
        )

# Use certifi's CA bundle for MongoDB Atlas SSL
ca_file = certifi.where()

# Initialize AsyncIOMotorClient with TLS
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=ca_file,
    # For development, allow self-signed certs (remove in production):
    tlsAllowInvalidCertificates=True,
    # Faster failure if network unreachable:
    serverSelectionTimeoutMS=5000,
)

# Select the database
db = client[db_name]