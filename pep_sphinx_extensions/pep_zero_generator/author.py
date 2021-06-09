from __future__ import annotations

from typing import NamedTuple


class _Name(NamedTuple):
    mononym: str = None
    forename: str = None
    surname: str = None
    suffix: str = None


class Author(NamedTuple):
    """Represent PEP authors."""
    last_first: str  # The author's name in Surname, Forename, Suffix order.
    nick: str  # Author's nickname for PEP tables. Defaults to surname.
    email: str  # The author's email address.


def parse_author_email(author_email_tuple: tuple[str, str], authors_overrides: dict[str, dict[str, str]]) -> Author:
    """Parse the name and email address of an author."""
    name, email = author_email_tuple
    _first_last = name.strip()
    email = email.lower()

    if _first_last in authors_overrides:
        name_dict = authors_overrides[_first_last]
        last_first = name_dict["Surname First"]
        nick = name_dict["Name Reference"]
        return Author(last_first, nick, email)

    name_parts = _parse_name(_first_last)
    if name_parts.mononym is not None:
        return Author(name_parts.mononym, name_parts.mononym, email)

    if name_parts.surname[1] == ".":
        # Add an escape to avoid docutils turning `v.` into `22.`.
        name_parts.surname = f"\\{name_parts.surname}"

    if name_parts.suffix is not None:
        last_first = f"{name_parts.surname}, {name_parts.forename}, {name_parts.suffix}"
        return Author(last_first, name_parts.surname, email)

    last_first = f"{name_parts.surname}, {name_parts.forename}"
    return Author(last_first, name_parts.surname, email)


def _parse_name(full_name: str) -> _Name:
    """Decompose a full name into parts.

    If a mononym (e.g, 'Aahz') then return the full name. If there are
    suffixes in the name (e.g. ', Jr.' or 'II'), then find and extract
    them. If there is a middle initial followed by a full stop, then
    combine the following words into a surname (e.g. N. Vander Weele). If
    there is a leading, lowercase portion to the last name (e.g. 'van' or
    'von') then include it in the surname.

    """
    possible_suffixes = {"Jr", "Jr.", "II", "III"}

    pre_suffix, _, raw_suffix = full_name.partition(",")
    name_parts = pre_suffix.strip().split(" ")
    num_parts = len(name_parts)
    suffix = raw_suffix.strip()

    if num_parts == 0:
        raise ValueError("Name is empty!")
    elif num_parts == 1:
        return _Name(mononym=name_parts[0], suffix=suffix)
    elif num_parts == 2:
        return _Name(forename=name_parts[0].strip(), surname=name_parts[1], suffix=suffix)

    # handles rogue uncaught suffixes
    if name_parts[-1] in possible_suffixes:
        suffix = f"{name_parts.pop(-1)} {suffix}".strip()

    # handles von, van, v. etc.
    if name_parts[-2].islower():
        forename = " ".join(name_parts[:-2]).strip()
        surname = " ".join(name_parts[-2:])
        return _Name(forename=forename, surname=surname, suffix=suffix)

    # handles double surnames after a middle initial (e.g. N. Vander Weele)
    elif any(s.endswith(".") for s in name_parts):
        split_position = [i for i, x in enumerate(name_parts) if x.endswith(".")][-1] + 1
        forename = " ".join(name_parts[:split_position]).strip()
        surname = " ".join(name_parts[split_position:])
        return _Name(forename=forename, surname=surname, suffix=suffix)

    # default to using the last item as the surname
    else:
        forename = " ".join(name_parts[:-1]).strip()
        return _Name(forename=forename, surname=name_parts[-1], suffix=suffix)
