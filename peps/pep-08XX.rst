PEP: 8XX
Title: Add timestamps to exception tracebacks
Author: Gregory P. Smith <greg@krypto.org>
PEP-Delegate:
Discussions-To: TODO
Status: Draft
Type: Standards Track
Created: 09-Sep-2025
Python-Version: 3.15
Post-History:


Abstract
========

This PEP proposes adding optional timestamps to Python exception objects that
can be displayed in tracebacks. When enabled, each exception will record the
time it was instantiated (typically when raised), and this timestamp can be
displayed alongside the exception message in formatted tracebacks. This feature
is particularly useful for debugging complex asynchronous applications, exception
groups, and distributed systems where understanding the temporal ordering of
exceptions is critical.


Motivation
==========

In modern Python applications, especially those using asynchronous programming
patterns and exception groups introduced in :pep:`654`, understanding the
temporal relationships between exceptions has become increasingly important.
Consider the following scenarios:

1. **Async servers with exception groups**: When multiple exceptions are caught
   and grouped together, it's often difficult to understand which exception
   occurred first and how they relate temporally to each other and to external
   events in the system.

2. **Distributed systems debugging**: When correlating exceptions across
   different services, having precise timestamps allows developers to match
   exceptions with logs from other systems, making root cause analysis more
   straightforward.

3. **Complex exception chains**: In applications with deep exception chains
   (exceptions raised during handling of other exceptions), timestamps help
   clarify the sequence of events that led to the final error state.

4. **Performance debugging**: Timestamps can reveal performance issues, such as
   delays between exception creation and handling, or help identify timeout-related
   problems.

Currently, developers must manually add timing information to exception messages
or use external logging frameworks, which can be cumbersome and inconsistent.
This PEP proposes a built-in, standardized approach.


Compelling Example: Async Service with Exception Groups
--------------------------------------------------------

Consider an async web service that fetches data from multiple backends
concurrently. When failures occur, understanding the timing is crucial for
diagnostics::

    import asyncio
    from datetime import datetime

    async def fetch_user_data(user_id: str):
        # Simulating a service that fails after 0.5 seconds
        await asyncio.sleep(0.5)
        raise ConnectionError(f"User service timeout for {user_id}")

    async def fetch_order_data(user_id: str):
        # Simulating a service that fails after 0.1 seconds
        await asyncio.sleep(0.1)
        raise ValueError(f"Invalid user_id format: {user_id}")

    async def fetch_recommendations(user_id: str):
        # Simulating a service that fails after 2.3 seconds
        await asyncio.sleep(2.3)
        raise TimeoutError(f"Recommendation service timeout")

    async def fetch_inventory(items: list):
        # Simulating a service that fails after 0.8 seconds
        await asyncio.sleep(0.8)
        raise KeyError(f"Item 'widget-42' not found in inventory")

    async def get_user_dashboard(user_id: str):
        """Fetch all user dashboard data concurrently."""
        async with asyncio.TaskGroup() as tg:
            user_task = tg.create_task(fetch_user_data(user_id))
            order_task = tg.create_task(fetch_order_data(user_id))
            rec_task = tg.create_task(fetch_recommendations(user_id))
            inv_task = tg.create_task(fetch_inventory(['widget-42']))

With ``PYTHON_TRACEBACK_TIMESTAMPS=iso``, the output would be::

    Traceback (most recent call last):
      ...
    ExceptionGroup: unhandled errors in a TaskGroup (4 sub-exceptions)
      +-+---------------- 1 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 11, in fetch_order_data
        |     raise ValueError(f"Invalid user_id format: {user_id}")
        | ValueError: Invalid user_id format: usr_12@34 <@2025-03-15T10:23:41.142857Z>
        +---------------- 2 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 7, in fetch_user_data
        |     raise ConnectionError(f"User service timeout for {user_id}")
        | ConnectionError: User service timeout for usr_12@34 <@2025-03-15T10:23:41.542901Z>
        +---------------- 3 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 19, in fetch_inventory
        |     raise KeyError(f"Item 'widget-42' not found in inventory")
        | KeyError: "Item 'widget-42' not found in inventory" <@2025-03-15T10:23:41.842856Z>
        +---------------- 4 ----------------
        | Traceback (most recent call last):
        |   File "service.py", line 15, in fetch_recommendations
        |     raise TimeoutError(f"Recommendation service timeout")
        | TimeoutError: Recommendation service timeout <@2025-03-15T10:23:43.342912Z>

From these timestamps, we can immediately see:

1. The ``ValueError`` from order validation failed first (at .142s)
2. The user service timed out 400ms later (at .542s)
3. The inventory service failed 300ms after that (at .842s)
4. The recommendation service was the slowest, timing out after 2.3 seconds (at 43.342s)

This temporal information is invaluable for debugging:

- We can see the order service fails fast with validation, suggesting a data
  quality issue rather than a performance problem
- The 2.3-second delay for recommendations indicates it might be the bottleneck
- The failures are spread across 3.2 seconds, showing they're not caused by a
  single systemic issue (like a network partition)
- We can correlate these timestamps with metrics from monitoring systems,
  load balancer logs, or database query logs

Without timestamps, we would only know that four services failed, but not
their temporal relationship, making root cause analysis significantly harder.


Rationale
=========

The decision to add timestamps directly to exception objects rather than using
alternative approaches (such as exception notes from :pep:`678`) was driven by
several factors:

1. **Performance**: Adding timestamps as notes would require creating string
   and list objects for every exception, even when timestamps aren't being
   displayed. The proposed approach stores a single integer (nanoseconds since
   epoch) and only formats it when needed.

2. **Consistency**: Having a standardized timestamp attribute ensures consistent
   formatting and behavior across the Python ecosystem.

3. **Backwards compatibility**: The feature is entirely opt-in, with no impact
   on existing code unless explicitly enabled.

4. **Simplicity**: The implementation is straightforward and doesn't require
   changes to exception handling semantics.


Specification
=============

Exception Timestamp Attribute
-----------------------------

A new attribute ``__timestamp_ns__`` will be added to the ``BaseException``
class. This attribute will store the time in nanoseconds since the Unix epoch
(same precision as ``time.time_ns()``) when the exception was instantiated.

- The attribute will be set to ``0`` by default (timestamps disabled)
- When timestamps are enabled, it will be set automatically during exception
  instantiation
- The timestamp represents when the exception object was created, which is
  typically when it was raised

Special Cases
-------------

To avoid performance impacts on normal control flow, timestamps will **not** be
collected for the following exception types even when the feature is enabled:

- ``StopIteration``
- ``AsyncStopIteration``

These exceptions are frequently used for control flow in iterators and async
iterators, and adding timestamps would introduce unnecessary overhead.

Configuration
-------------

The feature can be enabled through two mechanisms:

1. **Environment variable**: ``PYTHON_TRACEBACK_TIMESTAMPS``
   
   - ``"us"`` or ``"1"``: Display timestamps in microseconds
   - ``"ns"``: Display timestamps in nanoseconds  
   - ``"iso"``: Display timestamps in ISO 8601 format
   - Empty or unset: Timestamps disabled (default)

2. **Command-line option**: ``-X traceback_timestamps=<format>``
   
   Uses the same format options as the environment variable.

The command-line option takes precedence over the environment variable if both
are specified.

Display Format
--------------

When timestamps are enabled, they will be displayed at the end of exception
messages in tracebacks, using the format: ``<@timestamp>``

Example with ``PYTHON_TRACEBACK_TIMESTAMPS=iso``::

    Traceback (most recent call last):
      File "<stdin>", line 3, in california_raisin
        raise RuntimeError("not enough sunshine")
    RuntimeError: not enough sunshine <@2025-02-01T20:43:01.026169Z>
    
    During handling of the above exception, another exception occurred:
    
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
        california_raisin()
      File "<stdin>", line 5, in california_raisin
        raise OSError(2, "on a cloudy day")
    FileNotFoundError: [Errno 2] on a cloudy day <@2025-02-01T20:43:01.026176Z>

Traceback Module Updates
------------------------

The ``traceback`` module will be updated to support the new timestamp feature:

1. ``TracebackException`` class will gain a ``no_timestamp`` parameter
   (default ``False``) to control whether timestamps are displayed

2. Functions like ``print_exception()`` will gain a ``no_timestamp`` parameter
   to allow suppressing timestamp display even when globally enabled

3. The formatting functions will check the global configuration and the
   ``__timestamp_ns__`` attribute to determine whether and how to display
   timestamps

Python Configuration
--------------------

A new field ``traceback_timestamps`` will be added to ``PyConfig`` to store
the selected timestamp format. This will be accessible through
``sys.flags.traceback_timestamps``.


Backwards Compatibility
=======================

This proposal maintains full backwards compatibility:

1. The feature is disabled by default
2. Existing exception handling code continues to work unchanged
3. The new attribute is only set when the feature is explicitly enabled
4. Pickle/unpickle of exceptions works correctly with the new attribute
5. Third-party exception formatting libraries can ignore the attribute if desired


Security Implications
=====================

Timestamps in exceptions could potentially reveal information about:

1. System performance characteristics
2. Timing of operations that might be security-sensitive
3. Patterns of exception handling that could be used for timing attacks

However, since the feature is opt-in and primarily intended for development
and debugging, these concerns are minimal. Production systems concerned about
information leakage should not enable this feature.


How to Teach This
=================

The feature should be documented in:

1. The Python documentation for the ``exceptions`` module
2. The ``traceback`` module documentation
3. The Python tutorial section on exception handling (as an advanced topic)
4. The command-line interface documentation

Example use cases should focus on:

- Debugging async applications with multiple concurrent exceptions
- Correlating exceptions with external system logs
- Understanding performance issues in exception-heavy code


Reference Implementation
========================

The reference implementation is available in `CPython PR #129337
<https://github.com/python/cpython/pull/129337>`_.

The implementation includes:

- Core exception object changes to add the ``__timestamp_ns__`` attribute
- Traceback formatting updates to display timestamps
- Configuration through environment variables and command-line options
- Special handling for ``StopIteration`` and ``AsyncStopIteration``
- Comprehensive test coverage
- Documentation updates


Rejected Ideas
==============

Using Exception Notes
---------------------

An alternative approach would be to use the exception notes feature from
:pep:`678` to store timestamps. This was rejected because:

1. It would require creating string and list objects for every exception
2. The performance impact would be significant even when not displaying timestamps
3. It would make the timestamp less structured and harder to process programmatically

Always Collecting Timestamps
-----------------------------

Collecting timestamps for all exceptions unconditionally was considered but
rejected due to:

1. Performance overhead for exceptions used in control flow
2. Unnecessary memory usage for the vast majority of use cases
3. Potential security concerns in production environments

Millisecond Precision
---------------------

Using millisecond precision instead of nanosecond was considered, but
nanosecond precision was chosen to:

1. Match the precision of ``time.time_ns()``
2. Ensure sufficient precision for high-frequency exception scenarios
3. Allow for future use cases that might require sub-millisecond precision


Open Issues
===========

1. Should there be a Python API to programmatically enable/disable timestamps
   at runtime?

2. Should there be a way to retroactively add timestamps to existing exception
   objects?

3. Should the timestamp format be customizable beyond the predefined options?

4. **Always collecting timestamps vs. conditional collection**: Performance testing
   shows that collecting timestamps at exception instantiation time is cheap enough
   to do unconditionally. If we always collect them:

   - The ``__timestamp_ns__`` attribute would always exist, simplifying the
     implementation and making the pickle code cleaner (though pickled exceptions
     would be slightly larger)
   - Exceptions will unpickle cleanly on older Python versions (they'll just have
     an extra attribute that older versions ignore)
   - However, we don't currently have extensive testing for cross-version pickle
     compatibility of exceptions with new attributes. Should we add such tests?
     Is this level of compatibility testing necessary?

5. **Control flow exception handling**: The current implementation does not collect
   timestamps for ``StopIteration`` and ``AsyncStopIteration`` to avoid performance
   impact on normal control flow. Several questions arise:

   - Should this exclusion be configurable at runtime?
   - Should it apply to subclasses of these exceptions?
   - The check for these specific exceptions is in the hot path of exception
     creation and must be extremely fast. The current implementation uses a simple
     type check for performance. Adding complexity like subclass checks or a
     configurable tuple of excluded exceptions would impact performance. Is the
     current simple approach acceptable?


Acknowledgements
================

Thanks to Nathaniel J. Smith for the original idea suggestion, and to
dcolascione for initial review feedback on the implementation.


Footnotes
=========

References:

- `CPython PR #129337 <https://github.com/python/cpython/pull/129337>`_
- :pep:`654` -- Exception Groups and except*
- :pep:`678` -- Enriching Exceptions with Notes


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.