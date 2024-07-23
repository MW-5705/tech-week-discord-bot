import pymongo
from dotenv import load_dotenv
import os

mongo_url = os.getenv("mongo_url")

cluster = pymongo.MongoClient(mongo_url)