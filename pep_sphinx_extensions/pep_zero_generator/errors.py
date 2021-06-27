from __future__ import annotations

from pathlib import Path


class PEPError(Exception):
    def __init__(self, error: str, pep_file: Path, pep_number: int | None = None):
        super().__init__(error)
        self.filename = pep_file
        self.number = pep_number

    def __str__(self):
        error_msg = super(PEPError, self).__str__()
        error_msg = f"({self.filename}): {error_msg}"
        pep_str = f"PEP {self.number}"
        return f"{pep_str} {error_msg}" if self.number is not None else error_msg
