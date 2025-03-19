import redis
import json

class RedisQueue:
    def __init__(self, redis_url):
        self.redis = redis.from_StrictRedis.from_url(redis_url)
        self.key = 'customerio_analytics_queue'

    def qsize(self):
        return self.redis.llen(self.key)

    def put(self, item, block=True):
        self.redis.rpush(self.key, json.dumps(item))

    def get(self, block=True):
        item = self.redis.lpop(self.key)
        if item:
            return json.loads(item)
        return None

    def task_done(self):
        # No-op since Redis doesn't need explicit task completion tracking
        pass

    def join(self):
        while self.qsize() > 0:
            pass