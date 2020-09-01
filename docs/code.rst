Code Overview
=============
The Base Module
---------------
.. inheritance-diagram:: src.base
   :parts: 1
   :top-classes: src.base.AbstractStorage src.base.FilterBase

.. .. uml:: src/base.py
   Need to figure out how to use the uml package.


.. automodule:: src.base
   :members:
   :inherited-members:
   :show-inheritance:
   :undoc-members:

The Redis Module
----------------

.. inheritance-diagram:: src.redis
    :parts: 1

.. doctest::

    >>> from src.redis import RedisConnectionPool
    >>> store = RedisConnectionPool(port=8002)
    >>> from src.base import Reference
    >>> ref = Reference("redis", "foo")
    >>> store.put(ref, "hello")
    >>> store.get(ref)
    b'hello'
    >>> store.delete_at(ref)

.. automodule:: src.redis
   :members:
   :inherited-members:
   :show-inheritance:
   :undoc-members:
