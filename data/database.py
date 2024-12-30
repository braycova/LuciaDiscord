import os
import pymongo
from dotenv import load_dotenv
from random import randint

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_DB"))
db = client['Lucia']

calendar = db['calendar']
economy = db['economy']
shop = db['shop']
warnings = db['warnings']

def find_item_with_id(collection, value):
    return collection.find_one({'_id': value})


def find_item_with_value(collection, column, value):
    return collection.find_one({column: value})


def get_random_response(response_type):
    doc = db['responses'].find_one({"type": response_type})
    responses = doc['responses']
    index = randint(0, len(responses) - 1)
    return responses[index], index
