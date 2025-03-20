import redis
import json
import queue

class RedisQueue:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.key = 'customerio_analytics_queue'

    def qsize(self):
        return self.redis.llen(self.key)

    def put(self, item, block=True):
        self.redis.rpush(self.key, json.dumps(item))

    def get(self, block=True, timeout=None):
        if block:
            item = self.redis.blpop(self.key, timeout=timeout)
            if item:
                # blpop returns tuple of (key, value)
                return json.loads(item[1])
        else:
            item = self.redis.lpop(self.key)
            if item:
                return json.loads(item)
        raise queue.Empty  # Raise queue.Empty exception when queue is empty

    def task_done(self):
        # No-op since Redis doesn't need explicit task completion tracking
        pass

    def join(self):
        while self.qsize() > 0:
            pass