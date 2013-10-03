from depl import deploy
from depl.deploy import redis


def test_redis_dependencies():
    redis_settings = {}
    dependencies, commands = redis.load(redis_settings, deploy._Package)
    assert dependencies == set(['redis'])
    assert commands == []
