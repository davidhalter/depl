from os.path import dirname, abspath, join
import sys

import requests

from test_main import config_file, move_dir_content, main_run


def flask_depl(tmpdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'flask')
    move_dir_content(flask_path, str(tmpdir))
    main_run(['depl', 'deploy', 'localhost'])
    return "Hello World!"  # http resulting text


@config_file('''
    deploy:
        - python:
            port: 8888
            wsgi: hello:app
            ssl:
                port: 444
    ''')
def test_flask_simple(tmpdir):
    txt = flask_depl(tmpdir)
    assert requests.get("http://localhost:8888/").text == txt
    # ipv4
    assert requests.get("http://127.0.0.1:8888/").text == txt
    # ipv6
    if sys.version_info[:2] >= (2, 7):
        # broken stdlib causes this test to not work in py26:
        # https://github.com/shazow/urllib3/pull/203
        assert requests.get("http://[::1]:8888/").text == txt
        assert requests.get("https://[::1]:444/", verify=False).text == txt

    r = requests.get("https://127.0.0.1:444/", verify=False)
    assert r.text == txt
    assert r.history == []


@config_file('''
    deploy:
        - python:
            port: 8888
            wsgi: hello:app
            ssl:
                port: 444
                redirect: http
    ''')
def test_flask_redirects(tmpdir):
    txt = flask_depl(tmpdir)
    r = requests.get("http://localhost:8888/")
    assert r.text == txt
    assert r.history == []

    r = requests.get("https://127.0.0.1:444/", verify=False)
    assert r.text == txt
    assert len(r.history) == 1 and r.history[0].status_code == 301
