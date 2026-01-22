PEPs API
========

peps.json
---------

There is a read-only JSON document of every published PEP available at
https://peps.python.org/api/peps.json.

Each PEP is represented as a JSON object, keyed by the PEP number.
The structure of each JSON object is as follows:

.. code-block:: typescript

   {
     "<PEP number>": {
       "number": integer,  // always identical to <PEP number>
       "title": string,
       "authors": string,
       "discussions_to": string | null,
       "status": "Accepted" | "Active" | "Deferred" | "Draft" | "Final" | "Provisional" | "Rejected" | "Superseded" | "Withdrawn",
       "type": "Informational" | "Process" | "Standards Track",
       "topic": "governance" | "packaging" | "release" | "typing" | "",
       "created": string,
       "python_version": string | null,
       "post_history": string | null,
       "resolution": string | null,
       "requires": string | null,
       "replaces": string | null,
       "superseded_by": string | null,
       "author_names": Array<string>,
       "url": string
     },
   }

Date values are formatted as DD-MMM-YYYY,
and multiple dates are combined in a comma-separated list.

A selection of example PEPs are shown here,
illustrating some of the possible values for each field:

.. code-block:: json

   {
     "12": {
       "number": 12,
       "title": "Sample reStructuredText PEP Template",
       "authors": "David Goodger, Barry Warsaw, Brett Cannon",
       "discussions_to": null,
       "status": "Active",
       "type": "Process",
       "topic": "",
       "created": "05-Aug-2002",
       "python_version": null,
       "post_history": "`30-Aug-2002 <https://mail.python.org/archives/list/python-dev@python.org/thread/KX3AS7QAY26QH3WIUAEOCCNXQ4V2TGGV/>`__",
       "resolution": null,
       "requires": null,
       "replaces": null,
       "superseded_by": null,
       "author_names": [
        "David Goodger",
        "Barry Warsaw",
        "Brett Cannon"
       ],
       "url": "https://peps.python.org/pep-0012/"
     },
     "160": {
       "number": 160,
       "title": "Python 1.6 Release Schedule",
       "authors": "Fred L. Drake, Jr.",
       "discussions_to": null,
       "status": "Final",
       "type": "Informational",
       "topic": "release",
       "created": "25-Jul-2000",
       "python_version": "1.6",
       "post_history": null,
       "resolution": null,
       "requires": null,
       "replaces": null,
       "superseded_by": null,
       "author_names": [
        "Fred L. Drake, Jr."
       ],
       "url": "https://peps.python.org/pep-0160/"
     },
     "3124": {
       "number": 3124,
       "title": "Overloading, Generic Functions, Interfaces, and Adaptation",
       "authors": "Phillip J. Eby",
       "discussions_to": "python-3000@python.org",
       "status": "Deferred",
       "type": "Standards Track",
       "topic": "",
       "created": "28-Apr-2007",
       "python_version": null,
       "post_history": "30-Apr-2007",
       "resolution": null,
       "requires": "3107, 3115, 3119",
       "replaces": "245, 246",
       "superseded_by": null,
       "author_names": [
        "Phillip J. Eby"
       ],
       "url": "https://peps.python.org/pep-3124/"
     }
   }

release-cycle.json
------------------

There is a read-only JSON document of Python releases
available at https://peps.python.org/api/release-cycle.json.

Each feature version is represented as a JSON object,
keyed by the minor version number ("X.Y").
The structure of each JSON object is as follows:

.. code-block:: typescript

   {
     "<language version number>": {
       "branch": string,
       "pep": integer,
       "status": 'feature' | 'prerelease' | 'bugfix' | 'security' | 'end-of-life',
       "first_release": string,  // Date formatted as YYYY-MM-DD
       "end_of_life": string,  // Date formatted as YYYY-MM-DD
       "release_manager": string
     },
   }

For example:

.. code-block:: json

   {
     "3.15": {
       "branch": "main",
       "pep": 790,
       "status": "feature",
       "first_release": "2026-10-01",
       "end_of_life": "2031-10",
       "release_manager": "Hugo van Kemenade"
     },
     "3.14": {
       "branch": "3.14",
       "pep": 745,
       "status": "bugfix",
       "first_release": "2025-10-07",
       "end_of_life": "2030-10",
       "release_manager": "Hugo van Kemenade"
     }
   }

python-releases.json
--------------------

A more complete JSON document of all Python releases since version 1.6 is
available at https://peps.python.org/api/python-releases.json and includes
metadata about each feature release cycle, for example:

.. code-block:: json

   {
     "metadata": {
       "3.14": {
         "pep": 745,
         "status": "bugfix",
         "branch": "3.14",
         "release_manager": "Hugo van Kemenade",
         "start_of_development": "2024-05-08",
         "feature_freeze": "2025-05-07",
         "first_release": "2025-10-07",
         "end_of_bugfix": "2027-10-07",
         "end_of_life": "2030-10-01"
       }
     }
   }


And also detailed information about each individual release within that cycle,
for example:

.. code-block:: json

   {
     "releases": {
       "3.14": [
         {
           "stage": "3.14.0 candidate 3",
           "state": "actual",
           "date": "2025-09-18",
           "note": ""
         },
         {
           "stage": "3.14.0 final",
           "state": "actual",
           "date": "2025-10-07",
           "note": ""
         },
         {
           "stage": "3.14.1",
           "state": "expected",
           "date": "2025-12-02",
           "note": ""
         }
       ]
     }
   }

release-schedule.ics
--------------------

An iCalendar file of Python release dates is available at
https://peps.python.org/api/release-schedule.ics.
