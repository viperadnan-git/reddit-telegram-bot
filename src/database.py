from pymongo import MongoClient, ReturnDocument

from src.config import Config


class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.get_database("reddit-telegram-bot")
        self.users = self.db.get_collection("users")

    def update_user(self, user_id: str, data: dict) -> None:
        result = self.users.find_one_and_update(
            {"_id": user_id},
            {"$set": data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return result

    def get_user(self, user_id: str) -> dict:
        return self.users.find_one({"user_id": user_id})


db = Database()
