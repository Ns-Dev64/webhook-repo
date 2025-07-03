from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
events = db[COLLECTION_NAME]

def insert_event(data):
    events.insert_one(data)

def get_latest_events(limit=10):
    
    # sort the events with timestamps and return in descending order with applied limit
    return list(events.find().sort("timestamp", -1).limit(limit)) 
