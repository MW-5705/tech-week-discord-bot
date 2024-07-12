import pymongo
from dotenv import load_dotenv
import os

# mongo_url = os.getenv("MONGO_URL")
mongo_url = "mongodb://localhost:27017"
cluster = pymongo.MongoClient(mongo_url)