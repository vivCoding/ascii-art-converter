import redis
from rq import Worker, Queue, Connection
import os
import time

listen = ["default"]
redis_url = "redis://" + os.environ.get("REDIS_URL") +":6379"
connection = redis.from_url(redis_url)

def start_worker():
    worker = Worker(queue_class=Queue, queues=listen)
    worker.work()

if __name__ == "__main__":
    with Connection(connection):
        start_worker()