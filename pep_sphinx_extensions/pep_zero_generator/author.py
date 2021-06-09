from __future__ import annotations

from typing import NamedTuple
import unicodedata


class Name(NamedTuple):
    name: str = None  # mononym
    forename: str = None
    surname: str = None
    suffix: str = None


class Author:
    """Represent PEP authors.

    Attributes:
        last_first: The author's name in Surname, Forename, Suffix order.
        nick: Author's nickname for PEP tables. Defaults to surname.
        email: The author's email address.
        _first_last: The author's full name, unchanged

    """
    __slots__ = "last_first", "nick", "email", "_first_last"

    def __init__(self, author_email_tuple: tuple[str, str], authors_overrides: dict[str, dict[str, str]]):
        """Parse the name and email address of an author."""
        name, email = author_email_tuple
        self._first_last: str = name.strip()
        self.email: str = email.lower()

        self.last_first: str = ""
        self.nick: str = ""

        if self._first_last in authors_overrides:
            name_dict = authors_overrides[self._first_last]
            self.last_first = name_dict["Surname First"]
            self.nick = name_dict["Name Reference"]
        else:
            name_parts = self._parse_name(self._first_last)
            if name_parts.name is not None:
                self.last_first = self.nick = name_parts.name
            else:
                if name_parts.surname[1] == ".":
                    # Add an escape to avoid docutils turning `v.` into `22.`.
                    name_parts.surname = f"\\{name_parts.surname}"
                self.last_first = f"{name_parts.surname}, {name_parts.forename}"
                self.nick = name_parts.surname

            if name_parts.suffix is not None:
                self.last_first += f", {name_parts.suffix}"

    def __hash__(self):
        return hash(self.last_first)

    def __eq__(self, other):
        if not isinstance(other, Author):
            return NotImplemented
        return self.last_first == other.last_first

    def __len__(self):
        return len(unicodedata.normalize("NFC", self.last_first))

    @staticmethod
    def _parse_name(full_name: str) -> Name:
        """Decompose a full name into parts.

        If a mononym (e.g, 'Aahz') then return the full name. If there are
        suffixes in the name (e.g. ', Jr.' or 'III'), then find and extract
        them. If there is a middle initial followed by a full stop, then
        combine the following words into a surname (e.g. N. Vander Weele). If
        there is a leading, lowercase portion to the last name (e.g. 'van' or
        'von') then include it in the surname.

        """
        possible_suffixes = {"Jr", "Jr.", "II", "III"}

        pre_suffix, _, raw_suffix = full_name.partition(",")
        name_parts = pre_suffix.strip().split(" ")
        num_parts = len(name_parts)
        suffix = raw_suffix.strip() or None

        if num_parts == 0:
            raise ValueError("Name is empty!")
        elif num_parts == 1:
            return Name(name=name_parts[0], suffix=suffix)
        elif num_parts == 2:
            return Name(forename=name_parts[0].strip(), surname=name_parts[1], suffix=suffix)

        # handles rogue uncaught suffixes
        if name_parts[-1] in possible_suffixes:
            suffix = f"{name_parts.pop(-1)} {suffix}".strip()

        # handles von, van, v. etc.
        if name_parts[-2].islower():
            forename = " ".join(name_parts[:-2]).strip()
            surname = " ".join(name_parts[-2:])
            return Name(forename=forename, surname=surname, suffix=suffix)

        # handles double surnames after a middle initial (e.g. N. Vander Weele)
        elif any(s.endswith(".") for s in name_parts):
            split_position = [i for i, x in enumerate(name_parts) if x.endswith(".")][-1] + 1
            forename = " ".join(name_parts[:split_position]).strip()
            surname = " ".join(name_parts[split_position:])
            return Name(forename=forename, surname=surname, suffix=suffix)

        # default to using the last item as the surname
        else:
            forename = " ".join(name_parts[:-1]).strip()
            return Name(forename=forename, surname=name_parts[-1], suffix=suffix)
