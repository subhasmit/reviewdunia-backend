from rq import Queue

from app.db.redis import get_redis_client


def get_queue(name: str = "review-jobs") -> Queue:
    redis_client = get_redis_client()
    return Queue(name, connection=redis_client)
