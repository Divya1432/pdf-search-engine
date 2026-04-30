from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["acts_db"]
collection = db["acts"]