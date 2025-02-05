from pathlib import Path

import check_peps  # NoQA: inserted into sys.modules in conftest.py

from ..conftest import PEP_ROOT

PEP_9002 = Path(__file__).parent.parent / "peps" / "pep-9002.rst"


def test_with_fake_pep():
    content = PEP_9002.read_text(encoding="utf-8").splitlines()
    warnings = list(check_peps.check_peps(PEP_9002, content))
    assert warnings == [
        (1, "PEP must begin with the 'PEP:' header"),
        (6, "Must not have invalid header: Version"),
        (9, "Must not have duplicate header: Sponsor "),
        (10, "Must not have invalid header: Horse-Guards"),
        (15, "Must not have invalid header: Content-Type"),
        (1, "Must have required header: PEP"),
        (1, "Must have required header: Type"),
        (
            1,
            "Headers must be in PEP 12 order. Correct order: Title, Author, "
            "Sponsor, BDFL-Delegate, Discussions-To, Status, Topic, Requires, "
            "Created, Python-Version, Post-History, Resolution",
        ),
        (4, "Author continuation lines must end with a comma"),
        (5, "Author line must not be over-indented"),
        (7, "Python-Version major part must be 1, 2, or 3: 4.0"),
        (8, "Sponsor entries must begin with a valid 'Name': ''"),
        (9, "Sponsor entries must begin with a valid 'Name': ''"),
        (11, "Created must be a 'DD-mmm-YYYY' date: '1-Jan-1989'"),
        (12, "Delegate entries must begin with a valid 'Name': 'Barry!'"),
        (13, "Status must be a valid PEP status"),
        (14, "Topic must not contain duplicates"),
        (14, "Topic must be properly capitalised (Title Case)"),
        (14, "Topic must be for a valid sub-index"),
        (14, "Topic must be sorted lexicographically"),
        (16, "PEP references must be separated by comma-spaces (', ')"),
        (17, "Discussions-To must be a valid thread URL or mailing list"),
        (18, "Post-History must be a 'DD-mmm-YYYY' date: '2-Feb-2000'"),
        (18, "Post-History must be a valid thread URL"),
        (19, "Post-History must be a 'DD-mmm-YYYY' date: '3-Mar-2001'"),
        (19, "Post-History must be a valid thread URL"),
        (20, "Resolution must be a valid thread URL"),
        (23, "Use the :pep:`NNN` role to refer to PEPs"),
    ]


def test_skip_direct_pep_link_check():
    filename = PEP_ROOT / "pep-0009.rst"  # in SKIP_DIRECT_PEP_LINK_CHECK
    content = filename.read_text(encoding="utf-8").splitlines()
    warnings = list(check_peps.check_peps(filename, content))
    assert warnings == []
