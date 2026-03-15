PEP: 8XX
Title: Add timestamps to exceptions and tracebacks
Author: Gregory P. Smith <greg@krypto.org>
PEP-Delegate:
Discussions-To: TODO
Status: Draft
Type: Standards Track
Created: 15-March-2026
Python-Version: 3.15
Post-History:


Abstract
========

This PEP adds an optional ``__timestamp_ns__`` attribute to ``BaseException``
that records when the exception was instantiated.  When enabled via environment
variable or command-line flag, formatted tracebacks display this timestamp
alongside the exception message.


Motivation
==========

With the introduction of exception groups (:pep:`654`), Python programs can now
propagate multiple unrelated exceptions simultaneously.  When debugging these,
or when correlating exceptions with external logs and metrics, knowing *when*
each exception occurred is often as important as knowing *what* occurred.

Currently there is no standard way to obtain this information.  Developers must
manually add timing to exception messages or rely on logging frameworks, which
is inconsistent and error-prone.

Consider an async service that fetches data from multiple backends concurrently
using ``asyncio.TaskGroup``.  When several backends fail, the resulting
``ExceptionGroup`` contains all the errors but no indication of their temporal
ordering::

    import asyncio

    async def fetch_user(uid):
        await asyncio.sleep(0.5)
        raise ConnectionError(f"User service timeout for {uid}")

    async def fetch_orders(uid):
        await asyncio.sleep(0.1)
        raise ValueError(f"Invalid user_id format: {uid}")

    async def fetch_recommendations(uid):
        await asyncio.sleep(2.3)
        raise TimeoutError("Recommendation service timeout")

    async def fetch_inventory(items):
        await asyncio.sleep(0.8)
        raise KeyError("Item 'widget-42' not found in inventory")

    async def get_dashboard(uid):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_user(uid))
            tg.create_task(fetch_orders(uid))
            tg.create_task(fetch_recommendations(uid))
            tg.create_task(fetch_inventory(['widget-42']))

With ``PYTHON_TRACEBACK_TIMESTAMPS=iso``, the output becomes::

    Traceback (most recent call last):
      ...
    ExceptionGroup: unhandled errors in a TaskGroup (4 sub-exceptions)
      +-+---------------- 1 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 11, in fetch_orders
        |     raise ValueError(f"Invalid user_id format: {uid}")
        | ValueError: Invalid user_id format: usr_12@34 <@2025-03-15T10:23:41.142857Z>
        +---------------- 2 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 7, in fetch_user
        |     raise ConnectionError(f"User service timeout for {uid}")
        | ConnectionError: User service timeout for usr_12@34 <@2025-03-15T10:23:41.542901Z>
        +---------------- 3 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 19, in fetch_inventory
        |     raise KeyError("Item 'widget-42' not found in inventory")
        | KeyError: "Item 'widget-42' not found in inventory" <@2025-03-15T10:23:41.842856Z>
        +---------------- 4 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 15, in fetch_recommendations
        |     raise TimeoutError("Recommendation service timeout")
        | TimeoutError: Recommendation service timeout <@2025-03-15T10:23:43.342912Z>

The timestamps immediately reveal that the order validation failed first
(at .142s), while the recommendation service was the slowest at 2.3 seconds.
They can also be correlated with metrics dashboards, load balancer logs, or
traces from other services to build a complete picture of the incident.


Rationale
=========

The timestamp is stored as a single ``int64_t`` field in the ``BaseException``
C struct, recording nanoseconds since the Unix epoch.  This design was chosen
over using exception notes (:pep:`678`) because a struct field costs nothing
when not populated, avoids creating string and list objects at raise time, and
defers all formatting work to traceback rendering.  The feature is entirely
opt-in and does not change exception handling semantics.


Specification
=============

Exception Timestamp Attribute
-----------------------------

A new read/write attribute ``__timestamp_ns__`` is added to ``BaseException``.
It stores nanoseconds since the Unix epoch (same precision as
``time.time_ns()``) as a C ``int64_t`` exposed via a member descriptor.  When
timestamps are disabled, or for control flow exceptions (see below), the value
is ``0``.

Control Flow Exceptions
------------------------

To avoid performance impact on normal control flow, timestamps are **not**
collected for ``StopIteration`` or ``StopAsyncIteration`` even when the feature
is enabled.  These exceptions are raised at extremely high frequency during
iteration; the check uses C type pointer identity (not ``isinstance``) and adds
negligible overhead.

Configuration
-------------

The feature is enabled through CPython's two standard mechanisms:

``PYTHON_TRACEBACK_TIMESTAMPS`` environment variable
    Set to ``us`` or ``1`` for microsecond-precision decimal timestamps,
    ``ns`` for raw nanoseconds, or ``iso`` for ISO 8601 UTC format.
    Empty, unset, or ``0`` disables timestamps (the default).

``-X traceback_timestamps=<format>`` command-line option
    Accepts the same values.  Takes precedence over the environment variable.

A new ``traceback_timestamps`` field in ``PyConfig`` stores the selected format,
accessible as ``sys.flags.traceback_timestamps``.

Display Format
--------------

Timestamps are appended to the exception message line in tracebacks using
the format ``<@timestamp>``.  Example with ``iso``::

    Traceback (most recent call last):
      File "<stdin>", line 3, in california_raisin
        raise RuntimeError("not enough sunshine")
    RuntimeError: not enough sunshine <@2025-02-01T20:43:01.026169Z>

When colorized output is enabled, the timestamp is rendered in a muted color
to keep it visually distinct from the exception message.

Traceback Module Updates
------------------------

``TracebackException`` and the public formatting functions (``print_exception``,
``format_exception``, ``format_exception_only``) gain a ``no_timestamp``
keyword argument (default ``False``) that suppresses timestamp display even
when globally enabled.


Backwards Compatibility
=======================

The feature is disabled by default and does not affect existing exception
handling code.  The ``__timestamp_ns__`` attribute is always readable on
``BaseException`` instances, returning ``0`` when timestamps are not collected.

When timestamps are disabled, exceptions pickle in the traditional 2-tuple
format ``(type, args)``.  When a nonzero timestamp is present, exceptions
pickle as ``(type, args, state_dict)`` with ``__timestamp_ns__`` in the state
dictionary.  Older Python versions unpickle these correctly via
``__setstate__``.  Always emitting the 3-tuple form (with a zero timestamp)
would simplify the logic, but was avoided to keep the pickle output
byte-identical when the feature is off and to avoid any performance impact
on the common case.


Maintenance Burden
==================

The ``__timestamp_ns__`` field is a single ``int64_t`` in the ``BaseException``
C struct, present in every exception object regardless of configuration.  The
collection code is a guarded ``clock_gettime`` call; the formatting code only
runs at traceback display time.  Both are small and self-contained.

The main ongoing cost is in the test suite.  Tests that compare traceback
output literally need to account for the optional timestamp suffix.  Two
helpers are provided for this:

- ``traceback.strip_exc_timestamps(text)`` strips ``<@...>`` suffixes from
  formatted traceback strings.
- ``test.support.force_no_traceback_timestamps`` is a decorator that disables
  timestamp collection for the duration of a test.

Outside of the traceback-specific tests, approximately 14 of ~1230 test files
(roughly 1%) needed one of these helpers, typically tests that capture
``stderr`` and match against expected traceback output (e.g. ``test_logging``,
``test_repl``, ``test_wsgiref``, ``test_threading``).  The pattern follows the same approach used by ``force_not_colorized`` for
ANSI color codes in tracebacks.

Outside of CPython's own CI, where timestamps are enabled on a couple of
GitHub Actions runs to maintain coverage, most projects are unlikely to
have the feature enabled while running their test suites.


Security Implications
=====================

None.  The feature is opt-in and disabled by default.


How to Teach This
=================

The ``__timestamp_ns__`` attribute and configuration options will be documented
in the ``exceptions`` module reference, the ``traceback`` module reference,
and the command-line interface documentation.

This is a power feature: disabled by default and invisible unless explicitly
enabled.  It does not need to be covered in introductory material.


Reference Implementation
========================

`CPython PR #129337 <https://github.com/python/cpython/pull/129337>`_.


Rejected Ideas
==============

Using Exception Notes
---------------------

Using :pep:`678`'s ``.add_note()`` to attach timestamps was rejected for
several reasons.  Notes require creating string and list objects at raise time,
imposing overhead even when timestamps are not displayed.  Notes added when
*catching* an exception reflect the catch time, not the raise time, and in
async code this difference can be significant.  Not all exceptions are caught
(some propagate to top level or are logged directly), so catch-time notes
would be applied inconsistently.  A struct field captures the timestamp at the
source and defers all formatting to display time.

Always Collecting vs. Always Displaying
----------------------------------------

*Collecting* timestamps (a ``clock_gettime`` call during instantiation) and
*displaying* them in formatted tracebacks are separate concerns.

Always displaying was rejected because it adds noise that most users do not
need.  Always collecting (even when display is disabled) is cheap since the
``int64_t`` field exists in the struct regardless, but not collecting avoids
any potential for performance impact when the feature is turned off, and there
is no current reason to collect timestamps that will never be shown.  This could be
revisited if programmatic access to exception timestamps becomes useful
independent of traceback display.

Runtime API
-----------

A Python API to toggle timestamps at runtime is unnecessary complexity.
Applications that want timestamps are expected to enable them in their
environment; a runtime toggle would make it harder to reason about program
state.  The feature is configured at startup and remains fixed.

Custom Timestamp Formats
-------------------------

User-defined format strings would add significant complexity.  The three
built-in formats (``us``, ``ns``, ``iso``) cover the common needs:
human-readable decimal seconds, raw nanoseconds for programmatic use, and
ISO 8601 for correlation with external systems.

Configurable Control Flow Exception Set
-----------------------------------------

Allowing users to register additional exceptions to skip was rejected.  The
exclusion check runs in the hot path of exception creation and uses C type
pointer identity for speed.  Supporting a configurable set would require
either ``isinstance`` checks (too slow, walks the MRO) or a hash set of
type pointers (complexity with unclear benefit).  ``StopIteration`` and
``StopAsyncIteration`` are the only exceptions raised at frequencies where
the cost of ``clock_gettime`` is measurable.  If a practical need arises, an
API to register additional exclusions efficiently could be added as a follow-on
enhancement.

Millisecond Precision
---------------------

Nanosecond precision was chosen over millisecond to match ``time.time_ns()``
and to provide sufficient resolution for high-frequency exception scenarios.


Acknowledgements
================

Thanks to Nathaniel J. Smith for the original idea suggestion, and to
dcolascione for initial review feedback on the implementation.


References
==========

.. [1] `CPython PR #129337 <https://github.com/python/cpython/pull/129337>`_

.. [2] :pep:`654` -- Exception Groups and except*

.. [3] :pep:`678` -- Enriching Exceptions with Notes


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
