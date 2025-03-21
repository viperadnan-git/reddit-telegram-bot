from datetime import datetime
from typing import ClassVar, Optional

from pydantic import BaseModel, Field
from pymongo.collection import Collection


class RedditKeys(BaseModel):
    client_id: str
    client_secret: str


class User(BaseModel):
    id: int = Field(alias="_id", frozen=True)
    name: str
    username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    refresh_token: Optional[str] = None
    keys: Optional[RedditKeys] = None
    client: ClassVar[Collection]

    def save(self):
        self.updated_at = datetime.now()

        data = self.model_dump(by_alias=True)
        data.pop("_id")

        self.client.update_one(
            {"_id": self.id},
            {"$set": data},
            upsert=True,
        )
