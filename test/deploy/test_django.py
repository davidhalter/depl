import urllib

from test_main import config_file, run


@config_file('''
    deploy:
        - django:
            port: 8888
    ''')
def django(temp):
    run('depl deploy localhost')
    assert urllib.urlopen("http://localhost:8888/").getcode() == "django rocks"
