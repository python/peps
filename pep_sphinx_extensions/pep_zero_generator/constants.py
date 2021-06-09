"""Holds type and status constants for PEP 0 generation."""

STATUS_ACCEPTED = "Accepted"
STATUS_PROVISIONAL = "Provisional"
STATUS_REJECTED = "Rejected"
STATUS_WITHDRAWN = "Withdrawn"
STATUS_DEFERRED = "Deferred"
STATUS_FINAL = "Final"
STATUS_ACTIVE = "Active"
STATUS_DRAFT = "Draft"
STATUS_SUPERSEDED = "Superseded"

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

TYPE_STANDARDS = "Standards Track"
TYPE_INFO = "Informational"
TYPE_PROCESS = "Process"

# Valid values for the Type header.
TYPE_VALUES = {TYPE_STANDARDS, TYPE_INFO, TYPE_PROCESS}
# Active PEPs can only be for Informational or Process PEPs.
ACTIVE_ALLOWED = {TYPE_PROCESS, TYPE_INFO}
