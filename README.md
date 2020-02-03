# StorageCombinatorsPython
There is a quote from a scientist, whose name I can't remember that went like this.
> Over my career I've learned that some things don't have trade offs -- they're just better.
> These things don't come along very often, maybe once every five to ten years, but whenever I see one of these, I have learned to stop waffling and use it.

Storage Combinators is a better way of organizing, coordinating, and performing your storage related tasks in software.

This project serves as a library, and living reference to a simple way of architecting your storage.
90% of most modern applications are just shuffling data around.
Getting data from an API, saving the data to disk (for archiving/logging/observability), putting it in a cache, then putting it in a database.

Maintaining the core logic for this can get very hard.
Mess it up in one spot, and you have to invalidate your cache.
If you forget to use atomic writes in another spot, you can wind up with half written files that can't be deserialized.

Storage Combinators help with these issues and more relating to the persistence and access patterns of your data.

The Big Idea is this -- what if we just scaled down REST?
What if we just took our REST ideas, and scaled them down to a single process?
Caching already seems to work well.
The basic infrastructure seems to work well with regards to caching (which tends to be harder in most in memory processes).

If we do this, we wind up with Storage Combinators, as detailed by Marcel Weiher in [Storage Combinators](https://www.hpi.uni-potsdam.de/hirschfeld/publications/media/WeiherHirschfeld_2019_StorageCombinators_AcmDL_Preprint.pdf).

#### Goals and Features
Taken From [Things I believe](https://gist.github.com/stettix/5bb2d99e50fdbbd15dd9622837d14e2b).
1. A better system is often a smaller, simpler system.
2. To design healthy systems, divide and conquer. Split the problem into smaller parts.
3. Divide and conquer works recursively: divide the system into a hierarchy of simpler sub-systems and components.
   Corollary: When designing a system, there are more choices than a monolith vs. a thousand “microservices”.
4. Every inter-process boundary incurs a great cost, losing type safety, an making it much harder to reason about failures. Only introduce such boundaries where absolutely necessary and where the benefits outweigh the cost.
5. Telling what your system has done in the past is even more crucial, so make sure it’s auditable.
6. The physical manifestation of your system (e.g. choices of storage, messaging, RPC technology, packaging and scheduling etc) should usually be an implementation detail, not the main aspect of the system that the rest is built around.
7. It should be easy to change the underlying technologies (e.g. for data storage, messaging, execution environment) used by a component in your system, this should not affect large parts of your code base.
8. You should have at least two physical manifestations of your system: a fully integrated in-memory one for testing, and the real physical deployment. They should be functionally equivalent.
9. There is a running theme here: separate the description of what a system does from how it does it. This is probably the single most important consideration when creating a system.
10. Choose your data storage backend according to the shape of data, types of queries needed, patterns of writes vs. reads, performance requirements, and more. Every use case is different.
11. Being able to tell what your system is doing is crucial, so make sure it’s observable.
12. Telling what your system has done in the past is even more crucial, so make sure it’s auditable.

# Contribution Guidelines
Read the [Storage Combinators Paper](https://www.hpi.uni-potsdam.de/hirschfeld/publications/media/WeiherHirschfeld_2019_StorageCombinators_AcmDL_Preprint.pdf).
Think.
Fork.
Write tests.
Write code that tests them.
Push.

Right now this project needs
1. You.
2. More implementations of combinators in Python.
3. Use cases.
4. Better documentation.
5. Better copy.
6. More feedback on what doesn't make sense and what isn't working with respect to the project at large.
7. A better "Problem -Why - What - How" pitch.
8. Tests (we will likely have a decent to moderately complicated testing setup by the end using Jenkins due to possible atomic write issues with filesystems).

# Concerns We need to Address
Tracing (what path through the combinator tree did we take?)
Visualization (what does my storage tree look like?)
