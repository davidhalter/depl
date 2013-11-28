from pymongo import MongoClient

from test_main import config_file, main_run


@config_file('''
    deploy:
        - mongodb
    ''')
def test_simple(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
    client = MongoClient()
    db = client.test_database

    post = {
        "author": "Dini Mueter",
        "text": "Schwyzerdeutsch!"
    }
    _id = db.posts.insert(post)
    from_db = db.posts.find_one()
    assert from_db['author'] == "Dini Mueter"
    assert from_db['_id'] == _id
