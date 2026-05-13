from redis import Redis
from rq import Connection, Worker

from app.core.config import settings


if __name__ == "__main__":
    redis_connection = Redis.from_url(settings.redis_url)
    with Connection(redis_connection):
        worker = Worker(["review-jobs"])
        worker.work(with_scheduler=True)
