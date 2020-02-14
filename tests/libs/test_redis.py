import contextlib
import typing as t


import redis


@contextlib.contextmanager
def get_conn():
    pool = redis.ConnectionPool(host="localhost", port=8002)
    try:
        yield redis.Redis(connection_pool=pool)
    finally:
        pool.disconnect()


def test_login():
    with get_conn() as conn:
        pass


def test_semantics():
    with get_conn() as conn:
        conn.set("foo", 2)
        assert int(conn.get("foo")) == 2
        conn.delete("foo")
        assert conn.get("foo") is None
