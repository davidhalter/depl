from depl import deploy
from depl.deploy import redis
from depl.deploy import Package


def test_redis_dependencies():
    redis_settings = {}
    dependencies, commands = redis.load(redis_settings, deploy._Package)
    assert dependencies == set([Package('redis')])
    assert commands == []
