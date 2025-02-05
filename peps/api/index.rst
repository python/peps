PEPs API
========

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
       "post_history": string,
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
