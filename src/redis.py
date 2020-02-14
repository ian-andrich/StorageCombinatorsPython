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
        weakref.finalize(self, lambda s: s._conn_pool.close(), self)

    def get(ref):
        pass

    def put(ref, obj):
        pass

    def merge(ref, obj):
        pass

    def delete_at(ref, obj):
        pass
