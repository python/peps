"""
Validates the 'Created: ' field of PEPs match %d-%b-%Y as specified in PEP 1.

Requires Python 3.6+

Usage: python3 validate-created.py filename1 [filename2 [...]]
"""
import sys
from datetime import datetime as dt

COL_NUMBER = len("Created: ")


def validate_file(filename: str) -> int:
    errors = 0
    found = False
    line_number = 0

    with open(filename, encoding="utf8") as f:
        for line in f:
            line_number += 1
            if line.startswith("Created: "):
                found = True
                break

    if not found:
        errors += 1
        print(f"{filename}: 'Created:' not found")
        return errors

    date = line.split()[1]
    try:
        # Validate
        dt.strptime(date, "%d-%b-%Y")
    except ValueError as e:
        print(f"{filename}:{line_number}:{COL_NUMBER}: {e}")
        errors += 1

    return errors


def main(argv: list) -> None:
    assert len(argv) >= 2, "Missing required filename parameter(s)"
    total_errors = 0
    for filename in argv[1:]:
        total_errors += validate_file(filename)

    sys.exit(total_errors)


if __name__ == "__main__":
    main(sys.argv)
