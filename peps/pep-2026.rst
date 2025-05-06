PEP: 2026
Title: Calendar versioning for Python
Author: Hugo van Kemenade
Discussions-To: https://discuss.python.org/t/pep-2026-calendar-versioning-for-python/55782
Status: Rejected
Type: Process
Created: 11-Jun-2024
Python-Version: 3.26
Post-History: `14-Jun-2024 <https://discuss.python.org/t/pep-2026-calendar-versioning-for-python/55782>`__
Resolution: https://discuss.python.org/t/pep-2026-calendar-versioning-for-python/55782/126


Abstract
========

This PEP proposes updating the versioning scheme for Python to include
the calendar year.

Calendar Versioning (CalVer) makes *everything* easier to translate into
calendar time rather than counting versions and looking up when they will be
(or were) released:

* The support lifecycle is clear,
  making it easy to see when a version was first released.
* Deprecations are easier to manage for maintainers and users.
* It's easier to work out when a version will reach end of life (EOL).
* It helps people, especially new learners, understand how old their installation is.
* It's easier to reason about which versions of Python to support
  for libraries and applications.

Starting with what would have been Python 3.15,
the version is 3.YY.micro where YY is the year of initial release:

* Python 3.26 will be released in 2026 instead of Python 3.15.
  EOL is five years after initial release,
  therefore Python 3.26 will reach EOL in 2031.
* Python 3.27 will be released in 2027, and so on.

Motivation and rationale
========================

In 2019, we adopted an annual release cycle with :pep:`602`, which opened the
door for calendar versioning:

   Adopting an annual release calendar allows for natural switching to calendar
   versioning, for example by calling Python 3.9 “Python 3.20” since it’s
   released in October ‘20 and so on (“Python 3.23” would be the one released
   in October ‘23).

   While the ease of switching to calendar versioning can be treated as an
   advantage of an annual release cycle, this PEP does not advocate for or
   against a change in how Python is versioned. Should the annual release
   cycle be adopted, the versioning question will be dealt with in a separate
   PEP.

This is that PEP.

Current scheme
--------------

From the General Python FAQ:
:external+python:ref:`faq-version-numbering-scheme`

   Python versions are numbered "A.B.C" or "A.B":

   * *A* is the major version number
     -- it is only incremented for really major changes in the language.
   * *B* is the minor version number
     -- it is incremented for less earth-shattering changes.
   * *C* is the micro version number
     -- it is incremented for each bugfix release.

Python predates SemVer
----------------------

`Semantic Versioning <https://semver.org/>`__ (SemVer)
is a popular scheme which aims to communicate the intent of a release (though it
`doesn't always succeed <https://hynek.me/articles/semver-will-not-save-you/>`__).

   Given a version number MAJOR.MINOR.PATCH, increment the:

   1. MAJOR version when you make incompatible API changes
   2. MINOR version when you add functionality in a backward compatible manner
   3. PATCH version when you make backward compatible bug fixes

People often assume Python follows SemVer and
`complain <https://hugovk.github.io/python-calver/images/images.005.jpg>`__
`about <https://web.archive.org/web/20210415230926/https://twitter.com/gjbernat/status/1382833338751328257>`__
`breaking  <https://web.archive.org/web/20211116214312/https://twitter.com/VictorStinner/status/1460725106129489925>`__
`changes  <https://web.archive.org/web/20220311211508/https://twitter.com/brettsky/status/1502392549222223872>`__
in `feature <https://mastodon.social/@hugovk/111974066832803921>`__
`releases <https://fosstodon.org/@deshipu/112469856667396622>`__.
But Python predates SemVer by at least 15 years:
the SemVer spec was `introduced in 2009
<https://github.com/semver/semver.org/commit/ca645805ca206e83c7153c64f9bda54afff06262>`__
and the bespoke Python scheme was `added to source control in 1994
<https://github.com/python/cpython/commit/95f61a7ef067dbcabccc9b45ee885b0d55922c5f>`__
for the 1.0 release.

If Python adopted SemVer, that would imply a new major bump every year when
we remove deprecations.

Instead of SemVer, however, some projects have adopted another versioning
scheme based on the calendar.

Calendar versioning
-------------------

With `Calendar Versioning <https://calver.org/>`__ (CalVer),
you include some element of the date in the version number.
`For example <https://calver.org/users.html>`__,
Ubuntu and Black use the year and month -- Ubuntu 24.04 came out in April 2024;
pip and PyCharm use only the year.

.. list-table::
   :header-rows: 1

   * - Ubuntu
     - Black
     - pip
     - PyCharm
   * - YY.0M.micro
     - YY.MM.micro
     - YY.minor.micro
     - YYYY.minor.micro
   * - | 23.04
       | 23.10
       | 24.04
       | 24.10
     - | 23.12.1
       | 24.1.0
       | 24.1.1
       | 24.2.0
     - | 23.3
       | 23.3.1
       | 23.3.2
       | 24.0
     - | 2023.3.5
       | 2024.1
       | 2024.1.1
       | 2024.1.2

And here are some programming language standards,
all using some form of the year:

.. list-table::
   :header-rows: 1

   * - Ada
     - Algol
     - C
     - C++
     - Fortran
     - | ECMAScript
       | aka JavaScript
   * - YY / YYYY
     - YY
     - YY
     - YY
     - YY / YYYY
     - YYYY
   * - | 83
       | 95
       | 2012
       | 2022
     - | 58
       | 60
       | 68
     - | 89
       | 99
       | 11
       | 23
     - | 98
       | 03
       | 11
       | 23
     - | 66
       | 90
       | 2003
       | 2023
     - | 2020
       | 2021
       | 2022
       | 2023

Annual release cadence
----------------------

Since 2019, we've made a release each year:

* 3.15.0 will be released in 2026
* 3.16.0 will be released in 2027
* 3.17.0 will be released in 2028
* 3.18.0 will be released in 2029
* 3.19.0 will be released in 2030

This is sort of calendar-based, it’s just that it’s offset by 11 years.

CalVer for Python
-----------------

The simplest CalVer option would be to stick with major version 3,
and encode the year in the minor version:

* 3.26.0 will be released in 2026
* 3.27.0 will be released in 2027
* 3.28.0 will be released in 2028
* 3.29.0 will be released in 2029
* 3.30.0 will be released in 2030

For example, 3.26 will be released in 2026.
It makes it obvious when a release first came out.

Clarity of deprecation removal
------------------------------

Warnings for deprecations often mention the version they will be removed in.
For example:

   DeprecationWarning: 'ctypes.SetPointerType' is deprecated and slated for
   removal in Python 3.15

However, once aware of CalVer, it is immediately obvious from the warning how
long you have to take action:

   DeprecationWarning: 'ctypes.SetPointerType' is deprecated and slated for
   removal in Python 3.26

Clarity of support lifecycle
----------------------------

Right now, it’s a little tricky to work out when a release is end-of-life.
First you have to look up when it was initially released, then add 5 years:

   "When will Python 3.11 be EOL?"

   "Well, let's see... PEP 664 is the 3.11 release schedule, it says 3.11 was
   released in 2022, EOL after 5 years, so 2022 + 5 = 2027."

But if the initial release year is right there in the version,
it’s much easier:

    "When will Python 3.26 be EOL?"

    "26 + 5 = [20]31"

Clarity of installation age
---------------------------

With the year in the version, it’s easier to work out how old your installation
is. For example, with the current scheme, if you're using Python 3.15 in 2035,
it's not immediately clear that it was first released in 2026 (and has been EOL
since 2031).

With knowledge of CalVer, if you're using Python 3.26 in 2035, it's clear it was
first released nine years ago and it's probably time to upgrade.

This can help prompt people to switch to supported releases still under security
support, and help in teaching new users who may have older installations.

Clarity of version support
--------------------------

CalVer makes it easier to reason about which versions of Python to support.

For example, without CalVer, setting your minimum compatible Python version to
3.19 in 2031 sets an aggressive assumption regarding version adoption and
support.

However, with CalVer, this is more obvious if setting the minimum to 3.30 in
2031. For wider support, perhaps you prefer setting it to 3.26.

Similarly, library maintainers supporting all CPython upstream versions
need to test against five versions (or six including the pre-release).

For example, in 2030, the supported versions without CalVer would be:

* 3.15, 3.16, 3.17, 3.18, 3.19

With CalVer they would be:

* 3.26, 3.27, 3.28, 3.29, 3.30

A maintainer can see at a glance which versions are current and need testing.

Non-goals
---------

Like the current scheme, only the micro version will be incremented for bug
fix and security releases, with no change to the major and minor. For example:

.. list-table::
   :header-rows: 1

   * -
     - Current scheme
     - Proposed 3.YY.micro
   * - Initial release (Oct ’26)
     - 3.15.0
     - 3.26.0
   * - 1st bugfix release (Dec ’26)
     - 3.15.1
     - 3.26.1
   * - 2nd bugfix release (Feb ’27)
     - 3.15.2
     - 3.26.2
   * - ...
     - ...
     - ...
   * - Final security release (Oct ’31)
     - 3.15.17
     - 3.26.17

No change to :pep:`602` (Annual Release Cycle for Python):

* No change to the 17 months to develop a feature version: alphas, betas and
  release candidates.

* No change to the support duration:
  two years of full support and three years of security fixes.

* No change to the annual October release cadence.

Specification
=============

Python versions are numbered 3.YY.micro where:

* *3* is the major version number
  – it is always 3.

* *YY* is the minor version number
  - it is the short year number: ``{year} - 2000``.

* *micro* is the micro version number
  - it is incremented for each bugfix or security release.

We'll keep major version 3. Python 3 is the brand; there will be no Python 4.

In the year 2100, the minor will be ``2100-2000 = 100``,
therefore the version will be 3.100.0.

Python 3.14 will be the last version before this change, released in 2025.
Python 3.26 will be the first version after this change, released in 2026.
There will be no Python 3.15 to 3.25 inclusive.

Security implications
=====================

None known. No change to durations or timing of bug fix and security phases.

How to teach this
=================

We will announce this on blogs, in the 3.14 release notes, documentation,
and through outreach to the community.

This change targets the version following 3.14:
instead of 3.15 it will be 3.26.
This PEP was proposed in June 2024.
Development for the 3.15/3.26 release will begin in May 2025,
with the first alpha in October 2025 and initial release in October 2026.
We can already update documentation during the 3.14 cycle.
This gives plenty of notice.

We can make preview builds which only change the version for early testing.

We could ship a ``python3.15`` command as part of Python 3.26 that immediately
errors out and tells the user to use ``python3.26`` instead.

.. _PEP 2026 Rejected:

Rejected ideas
==============

.. _PEP 2026 YY.0:

YY.0
----

For example, Python 26.0 would be released in 2026.

There's `not much appetite for Python version 4
<https://www.techrepublic.com/article/programming-languages-why-python-4-0-will-probably-never-arrive-according-to-its-creator/>`__.
`We don’t want to repeat 2-to-3
<https://web.archive.org/web/20220906155615/https://twitter.com/gvanrossum/status/1306082472443084801>`__,
and 4 has a lot of expectations by now.
We don’t want “earth-shattering changes”.

Perhaps Python 4 could be reserved for something big like removing the GIL
(:pep:`703`),
but the Steering Council made it clear the `free-threading rollout must be gradual
<https://discuss.python.org/t/pep-703-making-the-global-interpreter-lock-optional-in-cpython-acceptance/37075>`__.
Will we stick with `version 3 forever
<https://discuss.python.org/t/python-3-13-alpha-1-contains-breaking-changes-whats-the-plan/37490/11>`__?

Another option would be to put the year in the major version and jump to 26.0.
This could mean we could leapfrog all that 4.0 baggage.

.. _PEP 2026 Platform compatibility tags:

Platform compatibility tags
'''''''''''''''''''''''''''

Changing the major version would complicate packaging, however.

The :ref:`packaging:platform-compatibility-tags` specification says the Python
version tag used in wheel filenames is given by
``sysconfig.get_config_var("py_version_nodot")``,
where the major and minor versions are joined together *without a dot*.
For example, 3.9 is ``39``.

During the 3.10 alpha, there was ambiguity because ``310`` can be interpreted
as 3.10, 31.0, or 310.

The specification says an underscore can be used if needed, and :pep:`641`
("Using an underscore in the version portion of Python 3.10 compatibility tags")
proposed this:

.. list-table::
   :header-rows: 1

   * -
     - Version → tag → version
     - PEP 641 proposed version
   * - Pre-3.10
     - 3.9 → ``39``
     -
   * - Ambiguity after 3.10
     - 3.10 → ``310`` → 3.10 or 31.0 or 310?
     - ``3_10``
   * - Ambiguity with YY.xx
     - 26.0 → ``260`` → 2.60 or 26.0 or 260?
     - ``26_0``

However, PEP 641 was `rejected
<https://discuss.python.org/t/pep-641-using-an-underscore-in-the-version-portion-of-python-3-10-compatibility-tags/5513/42>`__
because it was unknown what side effects there would be on code
we’re not aware of.

We would need something like this for YY.0 versioning,
which would be a significant amount of complex work.

.. _PEP 2026 Ecosystem changes:

Ecosystem changes
'''''''''''''''''

Would changing the major version to double digits break code?

Yes, any novel change to the version inevitably does because people make
assumptions, such as the major always being 3, or that the version parts are
always single digits. For example:

+-----------------+----------------------------------------------------+----------+--------+
| Version change  | Example                                            | Expected | Actual |
+=================+====================================================+==========+========+
| 2.7.9 → 2.7.10  | .. code-block:: python                             | 2.7.10   | 2.7.1  |
|                 |                                                    |          |        |
|                 |    'this is Python {}'.format(sys.version[:5])     |          |        |
+-----------------+----------------------------------------------------+----------+--------+
| 3.9 → 3.10      | .. code-block:: python                             | 3.10     | 3.1    |
|                 |                                                    |          |        |
|                 |    ".%s-%s" % (get_platform(), sys.version[0:3])   |          |        |
+-----------------+----------------------------------------------------+----------+--------+
| 3 → 4           | .. code-block:: python                             | 4.0      | 0      |
|                 |                                                    |          |        |
|                 |    if sys.version_info[1] >= 9:                    |          |        |
+-----------------+----------------------------------------------------+----------+--------+
| 3 → 26          | .. code-block:: python                             | 26       | 2      |
|                 |                                                    |          |        |
|                 |    if sys.version[0] == '3':                       |          |        |
+-----------------+----------------------------------------------------+----------+--------+

The last one here is most relevant for YY.0 versioning.
Therefore the 3.YY scheme is the safest and requires fewest changes,
because the *shape* of the version doesn't change:
it's still a 3 followed by two digits.

.. tip::

   Use
   `Ruff's YTT rules <https://docs.astral.sh/ruff/rules/#flake8-2020-ytt>`__ or
   `Flake8's flake8-2020 plugin <https://pypi.org/project/flake8-2020/>`__
   to help find the problems like these.

.. _PEP 2026 python3 command:

``python3`` command
'''''''''''''''''''

:pep:`394` (The “python” Command on Unix-Like Systems)
outlines recommendations for the ``python``, ``python2`` and ``python3``
commands. ``python`` can map to either ``python2`` or ``python3``.
These would need revisiting if the major version changed, and started changing annually.

Four years after Python 2.7's end-of-life, we could recommend ``python`` only
maps to the latest Python 3+ version.
But what would ``python3`` map to when Python 26.0 is out?
This would introduce additional complexity and cost.

CPython changes
'''''''''''''''

In addition to ``python3`` command changes, there are at least four places in
CPython that assume the major version is 3 and would need updating:

* `Lib/ast.py <https://github.com/python/cpython/blob/406ffb5293a8c9ca315bf63de1ee36a9b33f9aaf/Lib/ast.py#L50-L51>`__
* `Parser/pegen.c <https://github.com/python/cpython/blob/406ffb5293a8c9ca315bf63de1ee36a9b33f9aaf/Parser/pegen.c#L654-L658>`__
* `Parser/pegen.h <https://github.com/python/cpython/blob/406ffb5293a8c9ca315bf63de1ee36a9b33f9aaf/Parser/pegen.h#L284-L288>`__
* `Parser/string_parser.c <https://github.com/python/cpython/blob/406ffb5293a8c9ca315bf63de1ee36a9b33f9aaf/Parser/string_parser.c#L38-L43>`__

YY.0 rejection
''''''''''''''

The benefits of calendar versioning are not so big compared to the combined
costs for YY.0 versioning. Therefore, YY.0 versioning is rejected.

YY.MM
-----

For example, Python 26.10 would be released in October 2026.

Building upon YY.0 versioning, we could also include the release month as the minor
version, like Ubuntu and Black. This would make it clear *when* in the year it was
released, and also *when* in the year it will reach end-of-life.

However, YY.MM versioning is rejected for many of the same reasons as YY.0 versioning.

3.YYYY
------

For example, Python 3.2026 would be released in 2026.

It's clearer that the minor version is a year when using a four digits, and
avoids confusion with Ubuntu versions which use YY.MM.

``PY_VERSION_HEX``
''''''''''''''''''

CPython's C API :external+python:c:macro:`PY_VERSION_HEX` macro currently uses
eight bits to encode the minor version, accommodating a maximum minor version of
255. To hold a four-digit year, it would need to be expanded to 11 bits to fit
2047 or rather 12 bits for 4095.

This looks feasible, as it's intended for numeric comparisons, such as
``#if PY_VERSION_HEX >= ...``. In the `top 8,000 PyPI projects
<https://dev.to/hugovk/how-to-search-5000-python-projects-31gk>`__
only one instance was found of bit shifting
(``hexversion >> 16 != PY_VERSION_HEX >> 16``).

However, 3.YYYY is rejected as changing from two to four digits would
nevertheless need more work and break more code than simpler 3.YY versioning.

Editions
--------

For example, Python 3.15 (2026 Edition) would be released in 2026.

The Rust language uses
`"Editions" <https://doc.rust-lang.org/edition-guide/editions/>`__
to introduce breaking changes. Applying this to Python would require big
changes to :pep:`387` (Backwards Compatibility Policy) and is out of scope
for this PEP.

We could apply a year label to releases, such as "Python 3.15 (2026 Edition)",
but this is rejected because we'd have to keep track of *two* numbers.

Adopt SemVer and skip 4
-----------------------

For example, Python 5.0 would be released in 2026, 6.0 in 2027, and so on.

We could skip the problematic 4.0 entirely and adopt SemVer. Because
deprecations are removed in every feature release, we would get a new major
bump every year.

This is rejected because we wouldn't get the benefit of calendar versioning, and
moving away from 3.x would also `break code <PEP 2026 Ecosystem changes_>`_.

Change during 3.14 cycle
------------------------

The Python 3.14 release must go ahead because: π.

Backwards compatibility
=======================

This version change is the safest of the CalVer options considered
(see `rejected ideas <PEP 2026 rejected_>`_): we keep 3 as the major version,
and the minor version is still two digits.
The minor will eventually change to three digits but this is predictable,
a long way off and can be planned for.

We retain the ``python3`` executable.

Version mapping
---------------

Versions 3.15 to 3.25 inclusive will be skipped.
Features, deprecations and removals planned for these will be remapped to the
new version numbers.

For example, a deprecation initially planned for removal in 3.16 will instead
be removed in 3.27.

+-------------+------------------+-----------------+
| Old version | New version      | Initial release |
+=============+==================+=================+
| 3.14        | 3.14 (no change) | 2025            |
+-------------+------------------+-----------------+
| 3.15        | 3.26             | 2026            |
+-------------+------------------+-----------------+
| 3.16        | 3.27             | 2027            |
+-------------+------------------+-----------------+
| 3.17        | 3.28             | 2028            |
+-------------+------------------+-----------------+
| 3.18        | 3.29             | 2029            |
+-------------+------------------+-----------------+
| 3.19        | 3.30             | 2030            |
+-------------+------------------+-----------------+
| 3.20        | 3.31             | 2031            |
+-------------+------------------+-----------------+
| 3.21        | 3.32             | 2032            |
+-------------+------------------+-----------------+
| 3.22        | 3.33             | 2033            |
+-------------+------------------+-----------------+
| 3.23        | 3.34             | 2034            |
+-------------+------------------+-----------------+
| 3.24        | 3.35             | 2035            |
+-------------+------------------+-----------------+
| 3.25        | 3.36             | 2036            |
+-------------+------------------+-----------------+

Forwards compatibility
======================

Future change in cadence
------------------------

This PEP proposes no change to the annual release cadence as defined in
:pep:`602`, which lays out
:pep:`many good reasons for annual releases <602#rationale-and-goals>`
(for example, smaller releases with a predictable release calendar,
and syncing with external redistributors).
However unlikely, should we decide to change the cadence in the future, CalVer
does not preclude doing so.

Less frequent
'''''''''''''

If we went to *fewer than one release per year*, the proposed CalVer scheme
still works; indeed, it even helps people know in which year to expect the
release. For example, if we released every second year starting in 2036:

* 3.36.0 would be released in 2036
* 3.38.0 would be released in 2038
* and so on

Ecosystem changes depend in part on how the the hypothetical cadence-changing
PEP updates :pep:`387` (Backwards Compatibility Policy). If, for example, it
requires that the deprecation period must be at least one feature release and
not the current two (to maintain the minimum two years), CalVer has the benefit
over the status quo in requiring no changes to planned removal versions
(other than adjusting any falling in non-release years).

.. _PEP 2026 More frequent:

More frequent
'''''''''''''

If we went to *more than one release per year*, here are some options.
For example, if we released in April and October starting in 2036, the next
four releases could be:

+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| Scheme        | Notes                          | 2036 a    | 2036 b    | 2037 a    | 2037 b    |
+===============+================================+===========+===========+===========+===========+
| YY.MM.micro   | Year as major, month as minor  | 36.04.0   | 36.10.0   | 37.04.0   | 37.10.0   |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| YY.x.micro    | Year as major,                 | 36.1.0    | 36.2.0    | 37.1.0    | 37.2.0    |
|               | serial number as minor         |           |           |           |           |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| 3.YYMM.micro  | Combine year and month         | 3.3604.0  | 3.3610.0  | 3.3704.0  | 3.3710.0  |
|               | as minor                       |           |           |           |           |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| 3.YYx.micro   | Combine year and serial number | 3.360.0   | 3.361.0   | 3.370.0   | 3.371.0   |
|               | as minor                       |           |           |           |           |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| 3.YY.MM.micro | Add an extra month segment     | 3.36.04.0 | 3.36.10.0 | 3.37.04.0 | 3.37.10.0 |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| 3.major.micro | No more CalVer:                | 3.36.0    | 3.37.0    | 3.38.0    | 3.39.0    |
|               | increment minor                +-----------+-----------+-----------+-----------+
|               |                                | 3.50.0    | 3.51.0    | 3.52.0    | 3.53.0    |
|               |                                +-----------+-----------+-----------+-----------+
|               |                                | 3.100.0   | 3.101.0   | 3.102.0   | 3.103.0   |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+
| 4.major.micro | No more CalVer:                | 4.0.0     | 4.1.0     | 4.2.0     | 4.3.0     |
+---------------+ increment major                +-----------+-----------+-----------+-----------+
| 5.major.micro |                                | 5.0.0     | 5.1.0     | 5.2.0     | 5.3.0     |
+---------------+--------------------------------+-----------+-----------+-----------+-----------+

The YY options would require addressing issues around the
`platform compatibility tags <PEP 2026 platform compatibility tags_>`__,
the `python3 command <PEP 2026 python3 command_>`_, and code
`assuming the version always begins with 3 <PEP 2026 Ecosystem changes_>`__.

The options keeping major version 3 but changing the minor to three or four
digits would also need to address code
`assuming the version is always two digits <PEP 2026 Ecosystem changes_>`__.

The option adding an extra month segment is the biggest change as code would
need to deal with a four-part version instead of three.

The options dropping CalVer would be the most conservative
allowing the major and minor to be chosen freely.

No more CalVer
--------------

Adopting CalVer now does not preclude moving away CalVer in the future,
for example, back to the original scheme, to SemVer or another scheme.
Some options are `listed in the table above <PEP 2026 More frequent_>`__.
If wanting to make it clear the minor is no longer the year,
it can be bumped to a higher round number (for example, 3.50 or 3.100)
or the major version can be bumped (for example, to 4.0 or 5.0).
Additionally, a `version epoch
<https://packaging.python.org/en/latest/specifications/version-specifiers/#version-epochs>`__
could be considered.

Footnotes
=========

The author proposed calendar versioning at the `Python Language Summit 2024
<https://us.pycon.org/2024/events/language-summit/>`__;
this PEP is a result of discussions there and during PyCon US.

Read the `slides <https://hugovk.github.io/python-calver/>`__
and `blogpost
<https://pyfound.blogspot.com/2024/06/python-language-summit-2024-should-python-adopt-calver.html>`__
of the summit talk.

Acknowledgements
================

Thanks to Seth Michael Larson for the Language Summit Q&A notes and blogpost,
and to everyone who gave feedback at the summit and PyCon US.

Thank you to Łukasz Langa and Alex Waygood for reviewing a draft of this PEP.

Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
