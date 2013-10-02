import urllib
import psycopg2

from os.path import join, abspath, dirname
from test_main import config_file, main_run, move_dir_content


def delete_pg_connection():
    conn = psycopg2.connect("dbname='depl' user='depl' host='localhost' password='depl'")
    cur = conn.cursor()
    cur.execute("""DROP USER depl; DROP OWNED BY depl""")
    cur.execute("""DROP DATABASE depl;""")


def django_basic_test(tempdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'django_test')
    move_dir_content(flask_path, str(tempdir))
    main_run(['depl', 'deploy', 'localhost'])
    assert urllib.urlopen("http://localhost:8887/").read() == "django rocks\n"

    txt = urllib.urlopen("http://localhost:8887/static/something.txt").read()
    assert txt == "static files\n"
    # django plays with the db
    assert urllib.urlopen("http://localhost:8887/db_add.html").read() == "saved\n"


@config_file('''
    deploy:
        - django:
            port: 8887
    ''')
def test_django_sqlite(tempdir):
    django_basic_test(tempdir)
    content =  urllib.urlopen("http://localhost:8887/db_show.html").read()
    assert content == 'django.db.backends.sqlite3: 1'


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
def test_django_pg(tempdir):
    print "I am unable to connect to the database"
    django_basic_test(tempdir)
    # django plays with the db
    content = urllib.urlopen("http://localhost:8887/db_show.html").read()
    assert content == 'django.db.backends.psycopg2: 1'
    delete_pg_connection()
