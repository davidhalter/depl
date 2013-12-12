from os.path import join, abspath, dirname

from fabric.api import local
import requests

from ..helpers import config_file, main_run, move_dir_content


def delete_pg_connection():
    local("""sudo -u postgres psql -c "DROP DATABASE depl;" """)
    local("""sudo -u postgres psql -c "DROP USER depl;" """)


def copy_to_temp(tmpdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'django')
    move_dir_content(flask_path, str(tmpdir))


def django_basic_test(tmpdir):
    copy_to_temp(tmpdir)
    main_run(['depl', 'deploy', 'localhost'])
    assert requests.get("http://localhost:8887/").text == "django rocks\n"

    txt = requests.get("http://localhost:8887/static/something.txt").text
    assert txt == "static files\n"
    # django plays with the db
    assert requests.get("http://localhost:8887/db_add.html").text == "saved\n"


def django_pg_test(tmpdir):
    django_basic_test(tmpdir)
    # django plays with the db
    content = requests.get("http://localhost:8887/db_show.html").text
    assert content == 'django.db.backends.postgresql_psycopg2: 1\n'
    delete_pg_connection()


# actual tests
@config_file('''
    deploy:
        - django:
            port: 8887
    ''')
def test_django_sqlite(tmpdir):
    django_basic_test(tmpdir)
    content = requests.get("http://localhost:8887/db_show.html").text
    assert content == 'django.db.backends.sqlite3: 1\n'


@config_file('''
    deploy:
        - postgresql:
            database: depl
            user: depl
            password: depl
        - django:
            port: 8887
            settings: django_test.settings_with_db
    ''')
def test_django_pg(tmpdir):
    django_pg_test(tmpdir)


@config_file('''
    deploy:
        - django:
            port: 8887
            settings: django_test.settings_with_db
    ''')
def test_pg_auto_detection(tmpdir):
    django_pg_test(tmpdir)
