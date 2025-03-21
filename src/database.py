from pymongo import MongoClient

from src.config import Config
from src.models.user import User


class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.get_database("reddit-telegram-bot")
        self.users = self.db.get_collection("users")
        User.client = self.users

    def get_user(self, user_id: str) -> User:
        result = self.users.find_one({"_id": user_id})
        if not result:
            return None
        return User(**result)


db = Database()
