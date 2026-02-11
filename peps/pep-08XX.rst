PEP: 08XX
Title: Deprecate timedelta part attributes
Author: Anton Agestam
Status: Draft
Type: Standards Track
Created: 11-Feb-2026
Python-Version: 3.15

Abstract
========

This PEP proposes the deprecation and eventual removal of the ``.days``,
``.seconds``, and ``.microseconds`` attributes from ``datetime.timedelta``
objects. These attributes expose broken-down, partial pieces of a time
difference, and are a frequent source of bugs for users who mistake them
for unit representations of the total duration. We propose that these attributes
be phased out entirely. Users should instead rely on direct arithmetic with
``timedelta`` objects to extract specific components, eliminating the need to
expose leaked implementation details.


Motivation
==========

A regular problem encountered in Python codebases is the misuse of the
attributes on ``datetime.timedelta`` objects: ``.days``, ``.seconds``, and
``.microseconds``. Their naming easily misleads developers into believing
they represent the full, accumulated value of the object (akin to the
``.total_seconds()`` method). In reality, they represent broken-apart
pieces of a timedelta at different resolutions, which only make up the full
value when added together.

This issue surfaces frequently in code review and causes bugs in production systems.
The documentation for the ``.seconds`` attribute acknowledges this and
even contains a special warning call-out regarding this common mix-up.

Exposing exactly days, seconds, and microseconds is
arbitrary and leaks an implementation detail originating from 32-bit
Python 2 constraints. There is no consistent API access for other logical
time units—such as weeks, hours, minutes, or milliseconds. This also hinders
imaginable evolution of the timedelta type, for instance to support nanosecond
granularity.


Rationale
=========

Rather than attempting to rename the attributes or introduce new tuple-based
accessors, removing them entirely offers the most approachable way forward.
This approach for now avoids the task of designing a new interface for accessing
parts of a ``timedelta``. The existing arithmetic methods are deemed to work
well, but this PEP takes no stance on later introducing new methods to the
``timedelta`` object for improved ergonomics.

The ``datetime`` module already supports floor division between ``timedelta``
objects. The exact equivalent values of the current attributes can be
cleanly and explicitly derived via arithmetic:

* ``td.days`` is equivalent to ``td // timedelta(days=1)``
* ``td.seconds`` is equivalent to ``(td // timedelta(seconds=1)) % 86400``
* ``td.microseconds`` is equivalent to ``(td // timedelta(microseconds=1)) % 10**6``

Using timedelta arithmetic inherently protects the user from unit-confusion.
For example, to check if a delta is greater than 90 days, instead of writing
``if delta.days >= 90:``, the user can write the unambiguous
``if delta >= timedelta(days=90):``.

Removing these attributes also frees the internal representation of
``timedelta`` from its current historical constraints. If precision needs
to be improved in the future, e.g. adding nanosecond support, users could
simply divide by ``timedelta(nanoseconds=1)`` without the core developers
having to design new attributes.


Specification
=============

1. The ``.days``, ``.seconds``, and ``.microseconds`` attributes of
   ``datetime.timedelta`` will be scheduled for deprecation.

2. A long-term transition plan will be enacted:
   * **Phase 1 (Initial 5 years):** The properties will be decorated with
     ``@deprecated`` (e.g. ``@deprecated("Use timedelta arithmetic instead", category=None)``)
     to provide silent warnings that linters, type checkers, and IDEs can
     catch and flag to users well ahead of time.
   * **Phase 2 (Subsequent 5 years):** The deprecation category will be
     upgraded to trigger a runtime ``DeprecationWarning``.
   * **Phase 3:** The attributes can be removed completely, in accordance
     with the backwards compatibility policy outlined in PEP 387.

3. Official documentation will be updated to recommend ``.total_seconds()``
   for total duration, and arithmetic division with ``timedelta`` objects
   for unit extraction.


Backwards Compatibility
=======================

Because ``timedelta`` is widely used, deprecating these attributes will
impact existing codebases. To minimize disruption, this PEP stipulates a
long deprecation period as per PEP 387 (totaling 10 years) before ultimate
removal. This follows Python's normal deprecation cycle for widely used
standard library features, ensuring developers have ample time to migrate
without sudden breakage.


Rejected Ideas
==============

Rename attributes to ``.part_days``, ``.part_seconds``, etc.
------------------------------------------------------------
An `initial proposal <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/1>`_
suggested renaming the attributes to prefix them with ``part_`` to signify
they are incomplete fragments of the duration. This is rejected as the parts
themselves are arbitrary, and eliminating them entirely leaves a clean API. It
is deemed that these properties are not useful enough to warrant being part of
the API, and in the cases they are needed, they can still be calculated.

Return a tuple of internal values
---------------------------------
Suggestions were made to add a method returning the internally stored
values as a tuple, such as `(days, seconds, microseconds) <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/13>`_,
or a simplified ``(days, seconds)`` where seconds is a float. Others suggested
exporting a `5-tuple: (days, hours, mins, secs, microsecs) <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/4>`_.
This is similarly rejected due to being deemed of little value to users, as well
as because it exposes an internal implementation detail.

If timedelta precision is later improved to include nanoseconds, the size of the
tuple would have to change. Furthermore, the order of tuple components does not
inherently match constructor arguments. The arithmetic approach is safer and
more flexible.

Keep ``.days`` but deprecate the rest
-------------------------------------
Some `argued <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/21>`_
that ``.days`` should be kept because it is unbounded and does not have the
exact same "footgun" characteristics as ``.seconds``. This is rejected in part
for the sake of exposing a consistent API, and in part because the days
attribute has other footguns as `was pointed out in the discussion <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/22>`_:
``timedelta(seconds=-1).days == -1``.

Furthermore, the standard use case for ``.days``
(e.g. ``if delta.days >= 90``) is `better served <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/8>`_
by unambiguous ``timedelta`` object comparison: ``if delta >= timedelta(days=90)``.

Provide a ``__format__`` method
-------------------------------
A `tangential suggestion <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/10>`_
highlighted the difficulty of formatting ``timedelta`` objects into
human-readable strings, which often requires breaking down the parts, prompting
a request for a dedicated ``__format__`` method. While formatting is a valid
concern with high community demand, it is an orthogonal issue to the structural
representation of the class. This idea is explicitly deferred to future
independent design improvements of this type and considered out of scope of this
PEP.

Make microseconds a float part of seconds
-----------------------------------------
A `suggestion was raised <https://discuss.python.org/t/rename-alias-and-deprecate-timedelta-part-attributes/97674/12>`_
to eliminate the microseconds attribute by rolling it into seconds as a float.
This was rejected, as it is strictly an implementation detail and does not solve
the overarching issue of users mistaking partial properties for total accumulated
durations.
