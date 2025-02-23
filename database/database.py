import os
import threading
from pymongo import MongoClient

# Load configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# Initialize MongoDB
client = MongoClient(Config.DB_URI)
db = client['your_database_name']
collection = db['thumbnail']

# Threading lock for thread-safe operations
INSERTION_LOCK = threading.RLock()

# Function to add or update a thumbnail
async def df_thumb(id, msg_id):
    with INSERTION_LOCK:
        # Check if the thumbnail already exists
        thumb_data = collection.find_one({"id": id})
        if not thumb_data:
            # If it doesn't exist, create a new entry
            collection.insert_one({"id": id, "msg_id": msg_id})
        else:
            # If it exists, delete the old entry and add a new one
            collection.delete_one({"id": id})
            collection.insert_one({"id": id, "msg_id": msg_id})

# Function to delete a thumbnail
async def del_thumb(id):
    with INSERTION_LOCK:
        # Delete the thumbnail by ID
        collection.delete_one({"id": id})

# Function to fetch a thumbnail
async def thumb(id):
    # Fetch the thumbnail by ID
    return collection.find_one({"id": id})
