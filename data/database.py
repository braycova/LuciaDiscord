import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB"))
db = client['Lucia']


def find_item_with_id(collection, value):
    return collection.find_one({'_id': value})


def find_item_with_value(collection, column, value):
    return collection.find_one({column: value})
