from depl import deploy
from depl.deploy import redis


def test_redis_dependencies():
    redis_settings = {}
    dependencies, commands = redis.load(redis_settings, deploy._Package)
    assert dependencies == ['redis']
    assert commands == []
    commands = list(deploy.load('redis', redis_settings))
    assert len(commands) == 1 and 'redis' in commands[0]
