from pymongo import MongoClient

from ..helpers import config_file, main_run


@config_file('''
    deploy:
        - mongodb
    ''')
def test_simple(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
    client = MongoClient()
    db = client.depl_test_database

    post = {
        "author": "Dini Mueter",
        "text": "Schwyzerdeutsch!"
    }
    _id = db.posts.insert(post)
    try:
        from_db = db.posts.find_one()
        assert from_db['author'] == "Dini Mueter"
        assert from_db['_id'] == _id
        from_db = db.posts.find_one()
    finally:
        db.posts.remove()
    db.posts.find_one()
