from pymongo import MongoClient

from app.core.config import settings


_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.mongodb_uri, tz_aware=True)
    return _mongo_client


def get_mongo_db():
    return get_mongo_client()[settings.mongodb_db_name]
