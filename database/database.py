import os
import threading

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Load configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# Initialize SQLAlchemy
BASE = declarative_base()

def start() -> scoped_session:
    # Create the database engine
    engine = create_engine(Config.DB_URI, client_encoding="utf8")
    # Bind the metadata to the engine
    BASE.metadata.bind = engine
    # Create all tables if they don't exist
    BASE.metadata.create_all(engine)
    # Return a scoped session
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

# Create a global session object
SESSION = start()

# Threading lock for thread-safe operations
INSERTION_LOCK = threading.RLock()

# Define the Thumbnail table
class Thumbnail(BASE):
    __tablename__ = "thumbnail"
    id = Column(Integer, primary_key=True)
    msg_id = Column(Integer)

    def __init__(self, id, msg_id):
        self.id = id
        self.msg_id = msg_id

# Create the table if it doesn't exist
Thumbnail.__table__.create(checkfirst=True)

# Function to add or update a thumbnail
async def df_thumb(id, msg_id):
    with INSERTION_LOCK:
        # Check if the thumbnail already exists
        msg = SESSION.query(Thumbnail).get(id)
        if not msg:
            # If it doesn't exist, create a new entry
            msg = Thumbnail(id, msg_id)
            SESSION.add(msg)
            SESSION.flush()
        else:
            # If it exists, delete the old entry and add a new one
            SESSION.delete(msg)
            file = Thumbnail(id, msg_id)
            SESSION.add(file)
        # Commit the changes
        SESSION.commit()

# Function to delete a thumbnail
async def del_thumb(id):
    with INSERTION_LOCK:
        # Find and delete the thumbnail
        msg = SESSION.query(Thumbnail).get(id)
        if msg:
            SESSION.delete(msg)
            SESSION.commit()

# Function to fetch a thumbnail
async def thumb(id):
    try:
        # Fetch the thumbnail by ID
        t = SESSION.query(Thumbnail).get(id)
        return t
    finally:
        # Close the session
        SESSION.close()
