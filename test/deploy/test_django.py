import urllib

from depl import config
from depl.deploy import django
from os.path import join, abspath, dirname
from test_main import config_file, main_run, move_dir_content
from fabric.api import local


def delete_pg_connection():
    local("""sudo -u postgres psql -c "DROP DATABASE depl;" """)
    local("""sudo -u postgres psql -c "DROP USER depl;" """)


def copy_to_temp(tmpdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'django_test')
    move_dir_content(flask_path, str(tmpdir))


def django_basic_test(tmpdir):
    copy_to_temp()
    main_run(['depl', 'deploy', 'localhost'])
    assert urllib.urlopen("http://localhost:8887/").read() == "django rocks\n"

    txt = urllib.urlopen("http://localhost:8887/static/something.txt").read()
    assert txt == "static files\n"
    # django plays with the db
    assert urllib.urlopen("http://localhost:8887/db_add.html").read() == "saved\n"


def django_pg_test(tmpdir):
    django_basic_test(tmpdir)
    # django plays with the db
    content = urllib.urlopen("http://localhost:8887/db_show.html").read()
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
    content =  urllib.urlopen("http://localhost:8887/db_show.html").read()
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
    copy_to_temp(tmpdir)
    c = config.Config('depl.yml', None, None)
    settings = c.pools[0].deploy[0].settings
    dependencies, commands = django.load(settings, None)
    assert 'postgresql' in dependencies

    django_pg_test(tmpdir)
