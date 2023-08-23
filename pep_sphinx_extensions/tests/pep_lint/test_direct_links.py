import check_pep  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    "line",
    [
        "http://www.python.org/dev/peps/pep-0000/",
        "https://www.python.org/dev/peps/pep-0000/",
        "http://peps.python.org/pep-0000/",
        "https://peps.python.org/pep-0000/",
    ],
)
def test_check_direct_links_pep(line: str):
    warnings = [warning for (_, warning) in check_pep.check_direct_links(1, line)]
    assert warnings == ["Use the :pep:`NNN` role to refer to PEPs"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "http://www.rfc-editor.org/rfc/rfc2324",
        "https://www.rfc-editor.org/rfc/rfc2324",
        "http://datatracker.ietf.org/doc/html/rfc2324",
        "https://datatracker.ietf.org/doc/html/rfc2324",
    ],
)
def test_check_direct_links_rfc(line: str):
    warnings = [warning for (_, warning) in check_pep.check_direct_links(1, line)]
    assert warnings == ["Use the :rfc:`NNN` role to refer to RFCs"], warnings
