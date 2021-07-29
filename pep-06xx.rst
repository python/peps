PEP: 6xx
Title: Consistent views of namespaces
Author: Mark Shannon <mark@hotpy.org>
Status: Draft
Type: Standards
Content-Type: text/x-rst
Created: 30-Jul-2021
Post-History: XX-Aug-2021


Abstract
========

In early versions of Python, back in the 20th century, all namespaces,
whether in functions, classes or modules, were all implemented the same way,
as a dictionary.

For performance reasons, the implementation of function namespaces was changed.
Unfortunately this meant that the views of the namespaces, ``locals()`` and
``frame.f_locals``, ceased to be consistent and some odd bugs crept in over the years
as threads, generators and coroutines were added.

This PEP proposes make the views of namespaces consistent once more.
Modifications to ``locals()`` will be visible in the underlying variables,
``frame.f_locals`` will be consistent with ``locals()``, and they will all be
consistent regardless of threading or coroutines.

Motivation
==========

The current implementation of ``locals()`` and ``frame.f_locals`` is slow,
inconsistent and buggy.
We want to make it faster, consistent and most importantly fix the bugs.

For example::

    class C:
        x = 1
        locals()['x'] = 2
        print(x)

prints ``2``

but::

    def f():
        x = 1
        locals()['x'] = 2
        print(x)
    f()

prints ``1``

This is inconsistent, and confusing.
With this PEP both examples would print ``2``.

Worse than that, the current behavior can result in strange bugs [1]_

There are no compensating advantages for the current behavior;
it is unreliable and slow.

Rationale
=========

The current implementation of ``locals()``  and ``frame.f_locals``
returns a dictionary that is created on the fly from the array of
local variables. This can result in the array and dictionary getting
out of sync with each other. Writes to the ``locals()`` may not show
up as modifications to local variables. Writes to local variables can
get lost.

By making ``locals()`` and ``frame.f_locals`` return a view on the
underlying frame, these problems go away. ``locals()`` is always in
sync with the frame, because it is a view of it, not a copy of it.

Specification
=============

Python
------

``frame.f_locals`` will return a view object on the frame that
implements the ``collections.abc.Mapping`` interface.

``locals()`` will be defined simply as::

    def locals():
        return sys._getframe(0).f_locals


All writes to the ``f_locals`` mapping will be immediately visible
in the underlying variables. All changes to the underlying variables
will be immediately visible in the mapping. The ``f_locals`` will be a
full mapping, and can have arbitrary key-value pairs added to it.

For example::

    def test():
        x = 1
        locals()['x'] = 2
        locals()['y'] = 4
        locals()['z'] = 5
        y
        print(dict(locals()), x)

``test()`` will print ``{'x': 2, 'y': 4, 'z': 5} 2``

In 3.10, the above will fail with a ``NameError``, as the
definition of ``y`` by ``locals()['y'] = 4`` is lost.

C-API
-----

Two new C-API functions will be added::

    PyObject *PyEval_Locals(int depth)
    PyObject *PyFrame_GetLocals(PyFrameObject *f)

``PyEval_Locals(depth)`` is equivalent to: ``sys._getframe(depth).f_locals``
``PyFrame_GetLocals(f)`` is equivalent to: ``f.f_locals``

The existing  C-API function ``PyEval_GetLocals()`` will always raise an
exception with a message like::

    PyEval_GetLocals() is unsafe. Please use PyEval_Locals() instead.

This is necessary as ``PyEval_GetLocals()`` 
returns a borrowed reference which cannot be made safe.

Behavior of f_locals for optimized functions
--------------------------------------------

Although ``f.f_locals`` behaves as if it were the namespace of the function, 
some differences will be observable, 
most notably that ``f.f_locals is f.f_locals`` may be ``False``.

However ``f.f_locals == f.f_locals`` will be ``True``, and
all changes to the underlying variables, by any means, will be
always be visible.

Backwards Compatibility
=======================

Python
------

The current implementation has many corner cases and oddities.
Code that works around those may need to be changed.
Code that uses ``locals()`` for simple templating, or print debugging,
will continue to work correctly. Debuggers and other tools that use
``f_locals`` to modify local variables, will now work correctly,
even in the presence of threaded code, coroutines and generators.

C-API
-----

The change to ``PyEval_GetLocals()`` is a backwards compatibility break.
Code that uses  ``PyEval_GetLocals()`` will continue to operate safely, but
will need to be changed to use ``PyEval_Locals()`` to restore functionality.

This code::

    locals = PyEval_GetLocals();
    if (locals == NULL) {
        goto error_handler;
    }
    Py_INCREF(locals);

should be replaced with::

    locals = PyEval_Locals(0);
    if (locals == NULL) {
        goto error_handler;
    }


Reference Implementation
========================

TO DO.


Rejected Ideas
==============

[Why certain ideas that were brought while discussing this PEP were not ultimately pursued.]


Open Issues
===========

[Any points that are still being decided/discussed.]


References
==========

.. [1] https://bugs.python.org/issue30744

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
