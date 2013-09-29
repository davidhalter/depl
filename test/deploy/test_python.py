import urllib

from test_main import config_file, run


@config_file('''
    deploy:
        - python:
            port: 8888
    ''')
def test_flask(temp):
    run('depl deploy localhost')
    assert urllib.urlopen("http://localhost:8888/").getcode() == "flask as well"
