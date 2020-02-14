Tutorials
=========

The Hello World Demo
--------------------

Here we will set up a simple in memory store.

   >>> from src.base import *
   >>> store = DictStore()
   >>> ref = Reference("dict", "greeting")
   >>> entity = "Hello World!"
   >>> store.put(ref, entity)
   >>> print(store.get(ref))
   Hello World!

What have we done?

1. Initialized a store -- in this case a DictStore.
2. Chosen a reference for our entity (the string "Hello World!").  We have chosen the scheme for our reference to be 'dict', and the path to be 'greeting'.
3. Put our entity at the "address" given by the reference.
4. Retrieved the entity from the given address, then printed it.

This is the bare bones of how to work with Storage combinators.

They provide a way of addressing, storing, retrieving, updating, and deleting the entities in your system.

The 20 Second Elevator Pitch
----------------------------

Lets try something a little more complicated for those already losing interest.

    >>> from src.base import *
    >>> # Initialize the entity and references.
    >>> ref = Reference("entities", "greeting")
    >>> entity = "Hello world!"
    >>> # Initialize the base stores.
    >>> db = DictStore()
    >>> redis_cache = DictStore()
    >>> in_memory = DictStore()
    >>> # Set up the caching store.  Semantics for initialization are base_store, cache_store
    >>> first_cache = CacheStore(db, redis_cache)
    >>> top_level_store = CacheStore(first_cache, in_memory)
    >>> # Try putting something in there
    >>> top_level_store.put(ref, entity)
    >>> # Check all stores were updated with the single put to the top store
    >>> print(top_level_store.get(ref))
    Hello world!
    >>> print(in_memory.get(ref))
    Hello world!
    >>> print(first_cache.get(ref))
    Hello world!
    >>> print(redis_cache.get(ref))
    Hello world!
    >>> print(db.get(ref))
    Hello world!
    >>> # Now delete it
    >>> top_level_store.delete_at(ref)
    >>> # Check that it deleted references all the way down
    >>> top_level_store.get(ref)
    Traceback (most recent call last):
    ...
    KeyError: ('entities', 'greeting')
    >>> print(db.get(ref))
    Traceback (most recent call last):
    ...
    KeyError: ('entities', 'greeting')

Two levels of caching configured across three stores in 5 lines of code.

Let that sink in.

Storage combinators enable advanced syncing and caching of data with minimal effort.

A Little More Slowly Now
------------------------

Storage Combinators makes use of two broad classes of objects :class:`~src.base.Reference` and :class:`~src.base.AbstractStorage`

References play the role of URIs.
For those who haven't worked with them URIs are Uniform Resource Identifiers.
They serve to identify resources of interest.
They're like URLs but for stuff!

For our use case, we are interested in storages.

Resources are composed of a scheme and a path.
The scheme is application dependent.
You might have schemes ``in-memory``, ``redis``, and ``mariadb`` for a simple web app.
Larger apps might have a layered approach, with an ``entity`` scheme that has knowledge of and dispatches to ``customer-postgres`` ``customer-redis`` ``general-kafka`` etc. etc.
Put some thought into how you wish to use your scheme identifiers.

The path is like the path on your filesystem, or the url path.
It can be a flexible and safe way to address across your storage.
It is used to provide consistent object storage type semantics across your project.

Bear in mind for a single entity, you can have multiple paths operating on the entity, in much the same way an object can be retrieved from a database using many different queries.

The secret sauce is the Storage Combinators themselves.

They have REST semantics -- get, put, merge, delete_at.  It's just REST, and pipes and filters the whole way down.

A Tour of the Combinators
-------------------------

We have two main categories of Storage Combinators.

Pass Through Stores, and Mapping Stores.

Mapping Stores transform either the data or the URI.

Think of how we serialize our applications core data objects to JSON, or we translate them into a format that our ORM is happy with before we serialize them.

URI transformations are a more complicated topic, and relate more strongly to the architecture of your application.
Forgive us for putting this off for later.

For now just notice that it's potentially useful, to "redirect" people to storage resources.

OK, MappingStores serialize/deserialize (and redirect), PassThroughStores handle storage logic relating to caching and other storage concerns.

A couple of examples from the code include :class:`~src.base.PickleStore` and :class:`~src.base.JSONStore`.

Lets look at a few that actually **do something** interesting.
Currently we only have :class:`~src.base.DiskStoreText` and :class:`~src.base.DiskStoreBytes` implemented.

These write text and byte data directly to the disk.

Lets try using these ideas.

Lets say we wanted to pickle an object to a file on the disk, and keep an in memory store of it, for fast access.

   >>> import src.base
   >>> file_system = src.base.DiskStoreBytes()  # Base File system store -- defaults to current dir
   >>> pickle_mapper = src.base.PickleStore(file_system)  # Pickle Serializer
   >>> fs_mapper = src.base.FilePathMapper(pickle_mapper)  # File System set to the current directory
   >>> in_mem_cache = src.base.DictStore()  # In memory cache
   >>> store = src.base.CacheStore(fs_mapper, in_mem_cache)  # The combined store
   >>> data = "Storage check!"
   >>> ref = src.base.Reference("blah", "hello")
   >>> store.put(ref, data)  # Put the data in the store at the reference
   >>> in_mem_cache.get(ref) == data  # The in memory cache is working!
   True
   >>> fs_mapper.get(ref) == data  # It's on the filesystem
   True
   >>> import os
   >>> "hello" in os.listdir()  # Somethings on the disk!
   True
   >>> store.delete_at(ref)  # Ok, we're done now, kthnxbyeee
   >>> "hello" not in os.listdir()  # The file has been deleted
   True

Again it's only five lines to set up the core logic.

Lets go over what we did.
We used the mappers :class:`~src.base.PickleStore` and :class:`~src.base.FilePathMapper` to choose a src.base folder, and to map our object to the bytes serialized pickle format.
Then we persisted it to the disk using :class:`~src.base.DiskStoreBytes`.
Above that we had a cache for an in memory copy of our object.

Pipes and Filters
.................

Lets talk a bit about something we haven't gone over much.

Pipes and filters.

We've made some noise that **Storage Combinators** enable us to use a pipes and filters approach to programming.

The Pipes and Filters approach is enabled by the :class:`~src.base.LoggingStore` and :class:`~src.base.FilterBase` classes.
The logging store works like a regular combinator, but it holds a reference to :class:`~src.base.FilterBase` as a property.

:class:`~src.base.FilterBase` has a single method of interest :meth:`~src.base.Filterbase.write`.
Filters will overwrite this class to do something interesting with it.

You can use these to implement notifications, or provide a log of access to a store.
Frankly, theres a lot we can do with them, but lets focus on a simple one.

Let's say we are interested in access patterns for the store we implemented in the last example.

   >>> import src.base
   >>> file_system = src.base.DiskStoreBytes()  # Base File system store -- defaults to current dir
   >>> pickle_mapper = src.base.PickleStore(file_system)  # Pickle Serializer
   >>> fs_mapper = src.base.FilePathMapper(pickle_mapper)  # File System set to the current directory
   >>> in_mem_cache = src.base.DictStore()  # In memory cache
   >>> printing_filter = src.base.PrintFilter
   >>> store = src.base.CacheStore(fs_mapper, in_mem_cache)  # The combined store
   >>> print_filter = src.base.PrintFilter()  # The print filter
   >>> logged_store = src.base.LoggingStore(store, print_filter)  # The logging store
   >>> data = "Storage check!"
   >>> ref = src.base.Reference("blah", "hello")
   >>> logged_store.put(ref, data)
   <PutOperation op=PUT ref=<Reference scheme=blah path=hello>>
   >>> x = logged_store.get(ref)
   <GetOperation op=GET ref=<Reference scheme=blah path=hello>>
   >>> logged_store.delete_at(ref)
   <DeleteOperation op=DELETE ref=<Reference scheme=blah path=hello>>

Now we get them logged directly to our console on stdoud (channel 1).

We can implement other logs ourself by inspecting :class:`~src.base.PrintFilter` and overwriting its :meth:`~src.base.PrintFilter.write` method.
