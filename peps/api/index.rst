PEPs API
========

There is a read-only API of published PEPs available at:

* https://peps.python.org/api/peps.json

The structure is like:

.. code-block:: javascript

   {
     "<PEP number>": {
       "number": integer,
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
       "url": string
     },
   }

Date values are formatted as DD-MMM-YYYY,
and multiple dates are combined in a comma-separated list.

For example:

.. code-block:: json

   {
     "8": {
       "number": 8,
       "title": "Style Guide for Python Code",
       "authors": "Guido van Rossum, Barry Warsaw, Alyssa Coghlan",
       "discussions_to": null,
       "status": "Active",
       "type": "Process",
       "topic": "",
       "created": "05-Jul-2001",
       "python_version": null,
       "post_history": "05-Jul-2001, 01-Aug-2013",
       "resolution": null,
       "requires": null,
       "replaces": null,
       "superseded_by": null,
       "url": "https://peps.python.org/pep-0008/"
     },
     "484": {
       "number": 484,
       "title": "Type Hints",
       "authors": "Guido van Rossum, Jukka Lehtosalo, Łukasz Langa",
       "discussions_to": "python-dev@python.org",
       "status": "Final",
       "type": "Standards Track",
       "topic": "typing",
       "created": "29-Sep-2014",
       "python_version": "3.5",
       "post_history": "16-Jan-2015, 20-Mar-2015, 17-Apr-2015, 20-May-2015, 22-May-2015",
       "resolution": "https://mail.python.org/pipermail/python-dev/2015-May/140104.html",
       "requires": null,
       "replaces": null,
       "superseded_by": null,
       "url": "https://peps.python.org/pep-0484/"
     },
     "622": {
       "number": 622,
       "title": "Structural Pattern Matching",
       "authors": "Brandt Bucher, Daniel F Moisset, Tobias Kohn, Ivan Levkivskyi, Guido van Rossum, Talin",
       "discussions_to": "python-dev@python.org",
       "status": "Superseded",
       "type": "Standards Track",
       "topic": "",
       "created": "23-Jun-2020",
       "python_version": "3.10",
       "post_history": "23-Jun-2020, 08-Jul-2020",
       "resolution": null,
       "requires": null,
       "replaces": null,
       "superseded_by": "634",
       "url": "https://peps.python.org/pep-0622/"
     }
   }
