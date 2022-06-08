"""Holds type and status constants for PEP 0 generation."""

STATUS_ACCEPTED = "Accepted"
STATUS_ACTIVE = "Active"
STATUS_DEFERRED = "Deferred"
STATUS_DRAFT = "Draft"
STATUS_FINAL = "Final"
STATUS_PROVISIONAL = "Provisional"
STATUS_REJECTED = "Rejected"
STATUS_SUPERSEDED = "Superseded"
STATUS_WITHDRAWN = "Withdrawn"

# Valid values for the Status header.
STATUS_VALUES = {
    STATUS_ACCEPTED, STATUS_PROVISIONAL, STATUS_REJECTED, STATUS_WITHDRAWN,
    STATUS_DEFERRED, STATUS_FINAL, STATUS_ACTIVE, STATUS_DRAFT, STATUS_SUPERSEDED,
}
# Map of invalid/special statuses to their valid counterparts
SPECIAL_STATUSES = {
    "April Fool!": STATUS_REJECTED,  # See PEP 401 :)
}
# Draft PEPs have no status displayed, Active shares a key with Accepted
HIDE_STATUS = {STATUS_DRAFT, STATUS_ACTIVE}
# Dead PEP statuses
DEAD_STATUSES = {STATUS_REJECTED, STATUS_WITHDRAWN, STATUS_SUPERSEDED}

TYPE_INFO = "Informational"
TYPE_PROCESS = "Process"
TYPE_STANDARDS = "Standards Track"

# Valid values for the Type header.
TYPE_VALUES = {TYPE_STANDARDS, TYPE_INFO, TYPE_PROCESS}
# Active PEPs can only be for Informational or Process PEPs.
ACTIVE_ALLOWED = {TYPE_PROCESS, TYPE_INFO}

# map of topic -> additional description
SUBINDICES_BY_TOPIC = {
    "packaging": """\
The canonical, up-to-date packaging specifications can be found on the
`Python Packaging Authority`_ (PyPA) `Specifications page`_.
Packaging PEPs follow the `PyPA specification update process`_.
They are used to propose major additions or changes to the PyPA specifications.

.. _Specifications page: https://packaging.python.org/en/latest/specifications/
.. _Python Packaging Authority: https://www.pypa.io/
.. _PyPA specification update process: https://www.pypa.io/en/latest/specifications/#specification-update-process
""",
}
