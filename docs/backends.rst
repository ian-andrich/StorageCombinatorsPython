Backends Overview
=================

The backends aim to facilitate working with various storage engines.

What is a storage engine?  MySQL, Postgres, Kafka, Redis, etc.

Each of them have their own formatting quirks and persisting quirks, but the idea is simple.
We want to be able to map our Python Data Objects to a form (usually binary) that they are happy with.
Then we want to deserialize them back to our data objects.

We really don't want to think about serialization/deserialization in our core business logic.

.. warning::
   Here's an example.

   Every SQLAlchemy tutorial has you throwing around SQLAlchemy objects in your core application code.
   It has no business being there.
   You should control your core application, not someone else.

   Here's a better way -- serialize your data objects to SQLAlchemy's preferred formatting before writing.

   This takes discipline.

   Letting the Storage Combinators library do the heavy lifting keeps the serialization/deserialization where it should be.
   Behind the scenes.

We really want our storage logic to handle that.

In short a storage backend is -- **custom serialization in the form of** :class:`~src.base.BaseMapper` and **custom storage endpoints.**

Some of the backends may forego providing serializers and simply provide endpoints.
