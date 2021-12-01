from src import base
import weakref


try:
    import redis as r
except ImportError:
    r = None


def _if_imported(func):
    if r is not None:
        return func
    else:
        print("Couldn't find redis library")
        return None


@_if_imported
class RedisConnectionPool(base.StorageEndpoint):
    """
    This is the storage endpoint corresponding to a Redis ConnectionPool.

    It accepts arguments the same way as :class:`r.ConnectionPool` does.
    """

    def __init__(self, host="localhost", port=6379, db=0, **kwargs):
        self._conn_pool = r.ConnectionPool(host=host, port=port, db=db, **kwargs)
        # Make sure to close the connections just in case.
        weakref.finalize(self, lambda s: s._conn_pool.disconnect(), self)
        self.r = r.Redis(connection_pool=self._conn_pool)

    def get(self, ref):
        return self.r.get(ref.path)

    def put(self, ref, obj):
        self.r.set(ref.path, obj)

    def merge(self, ref, obj):
        pass

    def delete_at(self, ref):
        self.r.delete(ref.path)


__all__ = ["RedisConnectionPool"]