"""Holds type and status constants for PEP 0 generation."""

from enum import Enum


class PEPStatus(Enum):
    ACCEPTED = "Accepted"
    ACTIVE = "Active"
    DEFERRED = "Deferred"
    DRAFT = "Draft"
    FINAL = "Final"
    PROVISIONAL = "Provisional"
    REJECTED = "Rejected"
    SUPERSEDED = "Superseded"
    WITHDRAWN = "Withdrawn"


# Valid values for the Status header.
STATUS_VALUES = frozenset((status.value for status in PEPStatus))
# Map of invalid/special statuses to their valid counterparts.
SPECIAL_STATUSES = {
    "April Fool!": PEPStatus.REJECTED.value,  # See PEP 401 :)
}
# Draft PEPs have no status displayed.
HIDE_STATUS = frozenset({PEPStatus.DRAFT.value})
# Dead PEP statuses.
DEAD_STATUSES = frozenset(
    {PEPStatus.REJECTED.value, PEPStatus.WITHDRAWN.value, PEPStatus.SUPERSEDED.value}
)


class PEPType(Enum):
    INFO = "Informational"
    PROCESS = "Process"
    STANDARDS = "Standards Track"


# Valid values for the Type header.
TYPE_VALUES = frozenset((type_.value for type_ in PEPType))
# Active PEPs can only be for Informational or Process PEPs.
ACTIVE_ALLOWED = frozenset({PEPType.PROCESS.value, PEPType.INFO.value})

# Map of topic -> additional description.
SUBINDICES_BY_TOPIC = {
    "governance": """\
These PEPs detail Python's governance, including governance model proposals
and selection, and the results of the annual steering council elections.
    """,
    "packaging": """\
Packaging PEPs follow the `PyPA specification update process`_.
They are used to propose major additions or changes to the PyPA specifications.
The canonical, up-to-date packaging specifications can be found on the
`Python Packaging Authority`_ (PyPA) `specifications`_ page.

.. _Python Packaging Authority: https://www.pypa.io/
.. _specifications: https://packaging.python.org/en/latest/specifications/
.. _PyPA specification update process: https://www.pypa.io/en/latest/specifications/#specification-update-process
""",
    "release": """\
A PEP is written to specify the release cycle for each feature release of Python.
See the `developer's guide`_ for more information.

.. _developer's guide: https://devguide.python.org/devcycle/
""",
    "typing": """\
Many recent PEPs propose changes to Python's static type system
or otherwise relate to type annotations.
They are listed here for reference.
""",
}
