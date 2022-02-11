PEP: 6XX
Title: Immortal Objects, Using a Fixed Refcount
Author: Eric Snow <ericsnowcurrently@gmail.com>
PEP-Delegate: <TBD>
Discussions-To: python-dev@python.org
Status: Draft
Type: Informational
Created: 10-02-2022
Python-Version: 3.11
Post-History: 10-02-2022
Resolution: <TBD>


Abstract
========

Under this proposal, any object may be marked as immortal.
"Immortal" means the object will never be cleaned up (at least until
runtime finalization).  Specifically, the refcount for an immortal
object is set to a specific value, and that refcount is never
changed by ``Py_INCREF()`` or ``Py_DECREF()``.

Avoiding changes to the refcount is an essential part of this
proposal.  For what we call "immutable" objects, it makes them
truly immutable.  As described further below, this allows us
to avoid performance penalties in scenarios that
would otherwise be prohibitive.

This proposal is CPython-specific and, effectively, describes
internal implementation details.


Proposal
========

This approach involves these fundamental changes:

* add ``_Py_IMMORTAL_REFCNT`` (the magic value) to the internal C-API
* update ``Py_INCREF()`` and ``Py_DECREF()`` to no-op for objects with
  the magic refcount (or its most significant bit)
* update ``Py_SET_REFCNT()`` to do nothing to immortal objects
* ensure that all immortal objects are cleaned up during
  runtine finalization

Then setting any object's refcount to ``_Py_IMMORTAL_REFCNT``
makes it immortal.

(There are other minor, internal changes which are not described here.)

This is not meant to be a public feature but rather an internal one.
So the propsal does *not* including adding any new public C-API,
nor any Python API.  However, this does not prevent us from
adding (publicly accessible) private API to do things
like immortalize an object or tell if one
is immortal.


Motivation
==========

Without immortal objects, all objects are effectively mutable.  That
includes "immutable" objects like ``None`` and ``str`` instances.
This is because every object's refcount is frequently modified
as it is used during execution.

Consequently, CPU caches get invalidated for threads that share objects.
Similarly, copy-on-write gets triggered, e.g. in forked processes.
None of that would happen for objects that are truly immutable.
This has a concrete impact on some active projects
in the Python community.

For exmple, some large (enterprise) projects apply a pre-fork model,
where they get their applicationto the proper starting state and
then fork the process for each worker.  Their performance has
been affected and led to sub-optimal workarounds.

Another example is the effort to enable true multi-core Python execution
in CPython through a per-interpreter GIL.  Threads running code for
different interpreters cannot safely share any objects without
at least some sort of locking around refcount operations.
That means every interpreter would need its own
copy of *every* object, including the
singletons and builtin types.


Rationale
=========

The proposed solution is obvious enough that two people came to the
same conclusion (and implementation, more or less) independently.
Other designs were also considered.  Several possibilities
have also been discussed on python-dev in past years.

Alternatives include:

* use a high bit to mark "immortal" but do not change ``Py_INCREF()``
* add an explicit flag to objects
* implement via the type (``tp_dealloc()`` is a noop)
* track via the object's type object
* track with a separate table

Each of the above makes objects immortal, but none of them address
the performance penalties from refcount modification described above.

In the case of per-interpreter GIL, the only realistic alternative
is to move all global objects into ``PyInterpreterState`` and add
one or more lookup functions to access them.  Then we'd have to
add some hacks to the C-API to preserve compatibility for the
may objects exposed there.  The story is much, much simpler
with immortal objects


Impact
======

Benefits
--------

Most notably, the cases desribed in the two examples above stand
to benefit greatly from immortal objects.  Projects using pre-fork
can drop their workarounds.  For the per-interpreter GIL project,
immortal objects greatly simplifies the solution for existing static
types, as well as objects exposed by the public C-API.

Performance
-----------

The bare-minimum implementation shows a 4% slowdown. [benchmarks]_

Several mitigation strategies will be pursued in the effort to bring
it to performance-neutral.  This includes:

* mark all objects as immortal after runtime initialization but before
  running any user code
* specialize in the eval loop for immortal objects
  (especially the most commonly used objects like ``None``)

Also note that, when used with a pre-fork model, immortal objects
save a significant amount of memory.

Backward Compatibility
-----------------------

This proposal is completely compatible.  It is internal-only so no API
is changing.

The approach is also compatible with extensions compiled to the stable
ABI.  Unfortunately, they will modify the refcount and invalidate all
the performance benefits of immortal objects.  However, the high bit
of the refcount will still match ``_Py_IMMORTAL_REFCNT`` so we can
still identify such objects as immortal.

No user-facing behavior changes, with the following exceptions:

* code that inspects the refcount (e.g. ``sys.getrefcount()``
  or directly via ``ob_refcnt``) will see a really, really large
  value
* ``Py_SET_REFCNT()`` will be a noop for immortal objects

Neither should cause a problem.

Alternate Python Implementations
--------------------------------

This proposal is CPython-specific.

Security Implications
---------------------

This feature has no known impact on security.

Maintainability
---------------

This is not a complex feature so it should not cause much mental
overhead for maintainers.  The basic implementation doesn't touch
much code so it should have much impact on maintainabbility.  There
may be some extra complexity due to performance penalty mitigation.
However, that should be limited to where we immortalize all
objects post-init and that code will be in one place.

Non-Obvious Consequences
------------------------

* immortal containers effectively immortalize each contained item
* the same is true for objects held internally by other objects
  (e.g. ``PyTypeObject.tp_subclasses``)
* an immortal object's type is effectively immortal
* though extremely unlikely (and technically hard), any object could
  be incref'd enough to reach ``_Py_IMMORTAL_REFCNT`` and then
  be treated as immortal


Concerns
========

(This topic has been discussed previously on python-dev. [python-dev_])

Concerns have centered around the performance penalty.
Mitigation is discussed above.


Specification
=============

There isn't much more to say than what's in `Proposal`_ above.

Documentation
-------------

The feature will not be added to the documentation.  If ``Py_SET_REFCNT()``
were documented we would definitely add a note there.  At most we may
add a note to entries where it could be helpful for users to know
why they are seeing such a crazy-big refcount.  Currently there
is only one: ``sys.getrefcount()`` (and no affected
docs for the C-API).


How to Teach This
=================

This is not a user-facing change.


Deferred Functionality
======================

TBD


Reference Implementation
========================

A PR has been posted. [elizondo]_


Rejected Ideas
==============

TBD


Open Issues
===========

* how do we ensure all immortal objects get cleaned up during runtime finalization?
* how do we adjust ``sys.gettotalrefcount()`` to reflect things properly (for the sake of buildbots)?


References
==========

.. [benchmarks]
   https://github.com/python/cpython/pull/19474#issuecomment-1032944709
.. [elizondo]
   https://github.com/python/cpython/pull/19474
.. [python-dev]
   https://mail.python.org/archives/list/python-dev@python.org/thread/7O3FUA52QGTVDC6MDAV5WXKNFEDRK5D6/#TBTHSOI2XRWRO6WQOLUW3X7S5DUXFAOV
.. [python-dev-alt]
   https://mail.python.org/archives/list/python-dev@python.org/thread/PNLBJBNIQDMG2YYGPBCTGOKOAVXRBJWY


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.



..
    Local Variables:
    mode: indented-text
    indent-tabs-mode: nil
    sentence-end-double-space: t
    fill-column: 70
    coding: utf-8
    End:
