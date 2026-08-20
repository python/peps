:orphan:

.. _805-examples:

Appendix: Examples
==================

Tuple iterator
--------------

This example shows how an object can be made to appear as a synchronized object,
usable across multiple ThreadGroups, by using the ``protect`` mechanism.

Constructing thread safe programs with it is left as an exercise for the reader.

::

   from threading import Lock

   class SynchronizedTupleIter:

       def __init__(self, iterable):
           self.mutex = Lock()
           with self.mutex:
               self._iterator = self.mutex.protect(iter(iterable))
           self.__freeze__()

       def __iter__(self):
           return self

       def __next__(self):
           with self.mutex:
               return self._iterator.__next__()

Counter
-------

This example shows how to create a race-free Counter.
It is just to show how to use mutexes for race-free
operation. An efficient shared counter would need to use additional
mechanisms to avoid contention.


::

   class MutableInt:

       def __init__(self, value):
           self.value = value

   class Counter:

       def __init__(self):
           self.mutex = Lock()
           with self.mutex:
              self.number = self.mutex.protect(MutableInt(0))
           self.__freeze__()

       def value(self):
           with self.mutex:
               return self.number.value

       def increment(self, val):
           with self.mutex:
               self.number.value += 1

Unsafe Counter
--------------

Protection does not guarantee thread safety, it merely enforces the locking
discipline. While this makes it harder to accidentally make code that is
thread unsafe, it doesn't make it impossible. In this example, the ``increment``
method is not thread safe as another thread might modify the value between the
get and the set.

::

   class MutableInt:

       def __init__(self, value):
           self.value = value

   class Counter:

       def __init__(self):
           self.mutex = Lock()
           with self.mutex:
              self.number = self.mutex.protect(MutableInt(0))
           self.__freeze__()

       def value(self):
           with self.mutex:
               return self.number.value

       def set_value(self, val):
           with self.mutex:
               self.number.value = val

       def increment(self, val):
           val = self.value()
           self.set_value(val+1)

Bailing out instead of allowing races
-------------------------------------

For certain algorithms it may be impractical, or of little value, to
additionally guard against shared inputs. This PEP allows code to bail out of
an operation instead of dealing with concurrency. This may be the case for a
serialization library::

   def dump(mapping: dict):
       if mapping.__shareable__ is SYNCHRONIZED:
           raise ValueError("cannot cope with data races.")
       # other states are fine:
       #   LOCAL -- no concurrent accesses
       #   PROTECTED -- mutual exclusion prevents races
       #   IMMUTABLE -- no concurrent modifications
       for key, value in mapping.items():
           dump_one(key, value)


Serializing accesses to a file
------------------------------

Allowing multiple threads to write to the same file concurrently can only
produce non-deterministic behavior. Some simple serialization mechanisms can be
implemented::

   class ThreadSectionedFile:

       def __init__(self, f: file):
           self._lock = Lock()
           with self._lock:
               self._file = self.lock.protect(del f)
           self._sections: dict[Thread, list[bytes]] = dict().synchronized()

       def __enter__(self):
           self._sections[threading.current_thread()] = []
           # Note that the list is thread-local, no other thread may
           # inadvertently write into it.

       def write(self, data: bytes):
           me = threading.current_thread()
           if me not in self._sections:
               raise Exception("must call __enter__")
           self._sections[me].append(data)

       def __exit__(self, t, v, tb):
           data = self._sections[threading.current_thread()]
           del self._sections[threading.current_thread()]
           with self._lock:
               self._file.write(f"Thread {me.name} says:\n".encode())
               for d in data:
                   self._file.write(d)
               self._file.write(b"\n")
