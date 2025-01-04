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

def get_random_response(response_type):
    doc = db['responses'].find_one({"type": response_type})
    responses = doc['responses']
    index = randint(0, len(responses) - 1)
    return responses[index], index

def get_economy_profile(user_id):
    user = economy.find_one({"userId": user_id})
    if not user:
        new_user = {
            "userId": user_id,
            "balance": {
                "wallet": 200,
                "bank": 0,
                "storage": 3000
            },
            "inventory": {
                "Bank Note": 0
            }
        }
        doc = economy.insert_one(new_user)
        user = economy.find_one({"userId": doc.inserted_id})
    return user

def get_all_economy_profiles():
    return list(economy.find({"userId": {"$ne": "bank"}}))

def get_all_shop_items():
    return list(shop.find().sort("price", pymongo.ASCENDING))

def update_balance_value(user_id, field_name, value):
    economy.update_one({"userId": user_id}, {"$inc": {f"balance.{field_name}": value}})

def update_inventory_value(user_id, item_name, value):
    economy.update_one({"userId": user_id}, {"$inc": {f"inventory.{item_name}": value}})
