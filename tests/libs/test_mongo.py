import datetime


import pymongo


def get_conn() -> pymongo.MongoClient:
    return pymongo.MongoClient("localhost", 8003, username="root", password="example")


def test_connection():
    """Can get a connection"""
    with get_conn() as _:
        pass


def test_autoclose_connections():
    for _ in range(100):
        with get_conn():
            pass


def test_insertion():
    with get_conn() as client:
        db = client["test_libs_db"]
        collection = db["test_libs_collection"]
        # Hanging here.
        post = {
            "author": "Mike",
            "text": "My first blog post!",
            "tags": ["mongodb", "python", "pymongo"],
            "date": datetime.datetime.utcnow(),
        }
        # Mongodb silently hangs here if we are connecting on the wrong port
        result = collection.insert_one(post)
        result.inserted_id
