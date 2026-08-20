:orphan:

.. _805-implementation-details:

Appendix: Implementation
========================

Object state
------------

Recording the object's state and ID of the owning ThreadGroup or protecting
mutex requires space in the object header. The state can be encoded in a single
byte. The ID will need to handle all ThreadGroup and mutex IDs, so 16 bits
is unlikely to be sufficient. 32 bits will be enough.

With these fields, the ``PyObject`` header should be the smaller than is
currently implemented for :pep:`703`,
but larger than for the default (with GIL) build.

A possible object header:

.. code-block:: C

    uint32_t owner_id;
    uint32_t ref_count_shared;
    PyTypeObject *ob_type;
    uint8_t ref_count_local;  // For biased reference counting
    uint8_t state;
    uint16_t flags;
    uint32_t gc_info; // Additional info for the cycle GC

Reference counting
------------------

The author expects that the biased reference counting mechanism from :pep:`703`
will be used. Like :pep:`703`, per-thread reference counting and deferred
reference counting will also be used where necessary to minimize contention.

Checking object states
----------------------

CPython is a stack machine. That means that for a thread to acquire a reference
to an object, that object must come from the heap or an API call and be pushed
to the stack. In order to prevent C extensions seeing objects they should not,
all C API functions will need to validate their return value. In addition,
the interpreter will need to check any values it gets direct from the heap
before pushing them to the stack.

This is potentially a lot of new checks so, to avoid a large performance impact,
we need to keep the cost of these checks down. We can do that by:

* Making the checks cheap. Checks should consist of only one or two simple
  comparisons with minimal memory accesses.
* Removing as many checks as possible with static analysis in both the
  bytecode compiler and JIT compiler.

Specialization means that we can perform only one check for the most likely
state, rather than checking all legal states. If we expect a local object,
we just check the object's thread ID against the current ThreadGroup ID.
If, instead, we expect an immutable object,
we can just check that the object is immutable.

The JIT compiler can potentially remove redundant checks on the same object.

Access control function
'''''''''''''''''''''''

It is assumed that *local* objects will be the most likely, so if the
thread state is available, that will be checked first::

   PyObject *PyObject_CheckAccessThread(PyObject *op, PyThread t)
   {
       PyThreadState *tstate = PyThreadStateFromThread(t);
       if (op->owner_id == tstate->threadgroup_id) {
           return op;
       }
       if (op->state >= SYNCHRONIZED) {
           return op;
       }
       // Check for protected and stop the world cases...
   }

whereas if the thread is not as cheaply available, the shareable case
will be checked first::

   PyObject *PyObject_CheckAccess(PyObject *op)
   {
       if (op->state >= SYNCHRONIZED) {
           return op;
       }
       PyThreadState *tstate = PyThreadState_GET();
       if (op->owner_id == tstate->threadgroup_id) {
           return op;
       }
       // Check for protected and stop the world cases...
   }

It seems unlikely that many locks will be taken when other locks are already
held, as it is too easy to deadlock, so the set of held mutexes will be small
and can be implemented as a LIFO array (stack). Typically the matching mutex
for the object will be the first or second entry, so the check should be cheap.


C API
-----

For example, consider a hypothetical API function:
``PyObject *PyObject_Foo(PyObject *op)``.

To convert ``PyObject_Foo`` to support access control, the current
implementation would first be renamed ``PyObject_FooUnchecked``, then
``PyObject_Foo``` would then be implemented as::

   PyObject *
   PyObject_Foo(PyObject *op)
   {
       PyObject *result = PyObject_FooUnchecked(op);
       return _PyObject_CheckAccessNullable(result);
   }


where ``_PyObject_CheckAccessNullable`` is an internal function providing
the access control check. A ``_PyObject_CheckAccess`` variant would be
provided for when the object reference was known to not be ``NULL``.

This mechanical transformation is likely to leave some inefficiencies in the
code base, so additional work will be needed to re-optimized later.

Since all API functions need to check against the current thread,
new APIs taking a reference to the thread will be added to reduce the
overhead of fetching the thread reference on every call.
For example ``PyObject_GetAttr`` would gain a ``PyObject_GetAttrThread``
variant::

    PyObject *PyObject_GetAttrThread(PyObject *v, PyObject *name, PyThread t);

Variants of ``_PyObject_CheckAccess`` that take a thread pointer will be
added.

Many API functions will need no modification. For example, ``PyObject_Str``
always returns a ``str``, which are immutable, so no additional access check
is needed. ``PyObject_SetItem`` does not return an object, so will need no
additional check.


Interpreter
-----------

All code that loads from the heap will need access control.
Additionally some local variable loads will need checks.

We don't want to slow down local variable access, so we will rely on the
bytecode compiler to only insert checks where needed,
adding ``LOAD_FAST_MAYBE_UNPROTECTED`` instructions instead of ``LOAD_FAST``
where necessary.

Instructions that push references to the stack that reference objects that
originate from the heap, or C API, need to add checks.
This can be as simple as adding a check at the end of the instruction, using
micro-ops this can be as simple as adding the extra micro-op, eg::

   macro(LOAD_ATTR_MODULE) =
       unused/1 +
       _LOAD_ATTR_MODULE +
       POP_TOP +
       unused/5 +
       _PUSH_NULL_CONDITIONAL;

becomes:

   macro(LOAD_ATTR_MODULE) =
       unused/1 +
       _LOAD_ATTR_MODULE +
       POP_TOP +
       TOS_ACCESS_CHECK +
       unused/5 +
       _PUSH_NULL_CONDITIONAL;

Bytecode Compiler
-----------------

Because all values on the evaluation stack must be safe to access, and the
only way to store to a local variable is from the evaluation stack, it
might appear that all local variable accesses are safe.
However, this isn't quite the case: if a value is stored in a local
variable in a ``with`` statement, it might be unprotected outside of the
``with`` statement.

We don't want to slow down all local variable reads, so we have to do some
static analysis to insert additional checks where needed.
We already do these checks to use ``LOAD_FAST_CHECK`` only where necessary,
the apporach here is very similar.

The algorithm works as follows:

* Mark any local variable assigned in a ``with`` statement as "unprotected"
* Use data flow to detect where this flows to a ``LOAD_FAST``
* Replace any "unprotected" ``LOAD_FAST`` with ``LOAD_FAST_MAYBE_UNPROTECTED``
* Any ``LOAD_FAST_MAYBE_UNPROTECTED`` marks the local variable as protected
  again

Projecting from the prevalence of ``with`` statements and the effectiveness
of converting ``LOAD_FAST`` to ``LOAD_FAST_BORROW``, there should be a
vanishingly small number of ``LOAD_FAST``\s left as
``LOAD_FAST_MAYBE_UNPROTECTED``.

Synchronized, Frozen and Local Collections
------------------------------------------

We are adding three or four new classes that are very similar to existing
collections, and modifying the code for the existing collection classes.
We want to do this correctly and without adding much new code.

Take ``set`` as example (``dict`` and ``list`` are similar).
We need to add access controls to existing methods, and add a new class:
``SynchronizedSet``.

1. All three classes should use the same layout and C
   struct to describe that layout.
2. Non-mutating methods should be factored out into a core function
   with no synchronization, but with access control added.

  a. ``frozenset`` can use that implementation directly
  b. ``SyncronizedSet`` will need to acquire an internal mutex before
     calling the function, and release it afterwards
  c. ``set``, as it is local, can also use the base implementation directly

3. Mutating methods should also be factored out into a core function
   with no synchronization, but with access control added.

  a. ``frozenset`` will have no implementation of mutating methods
  b. ``SyncronizedSet`` will need to acquire a mutex before
     calling the function, and release it afterwards
  c. ``set``, as it is local, can use the base implementation directly

4. ``SyncronizedSet`` methods that take another synchronized object as
   an argument will need to ensure that the internal mutexes are taken in the
   correct order to avoid deadlock.

Optimizations
-------------

Reusing existing optimizations for local objects
''''''''''''''''''''''''''''''''''''''''''''''''

Because local objects are only accessible by one ``ThreadGroup``,
all current optimizations can be applied unchanged.

Stop the World (almost) Immutability
''''''''''''''''''''''''''''''''''''

Some objects, for example functions, are *synchronized* for backwards
compatibility reasons, but are rarely mutated.

These objects can be optimized in the JIT, with the same optimizations
that are already implemented for the with-GIL build, but using a
stop-the-world lock. Should any of these objects be mutated, all
other threads are stopped cooperatively. Once stopped, mutation happens.
The other threads see the stop-the-world event as a possible escape,
so will be guarded against the change.

Guard-free optimizations for immutable objects
''''''''''''''''''''''''''''''''''''''''''''''

We already take advantage of immutabilty for some optimizations,
but this is done in an ad-hoc fashion. With immutability becoming a
VM enforced property, we can use known immutability to perform
more guard removal in the JIT.

Implementation strategy
-----------------------

The major challenge in implementing this PEP will be to keep the default
build of CPython working while adding the capabilities of this PEP.
The two key features to be added are ThreadGroups and object ownership.
Without both, neither is useful.
Implementing ownership will require the ABI breakage discussed above.

With that in mind, here is a possible order of implementation:

* ThreadGroups
* One-time ABI breakage
* Port biased and deferred reference counting from the free-threading build
* Simple ownership. Local and immutable only
* Support parallel allocation and cyclic garbage collection
* ``__freeze__``
* Synchronized objects
* Protected object state, including bytecode compiler support
* ``TransferBox`` and ``Channel``
* ``sys.monitoring.StopTheWorld``
* Performance work

Validation
----------

In order to get both correctness and performance, this PEP provides a model
of execution that promises to be both sound and optimizable. To verify
that soundness in the context of optimizations in either the JIT or
interpreter, validation will be added in the debug builds at all points
when a reference is pushed to the stack in the interpreter.
