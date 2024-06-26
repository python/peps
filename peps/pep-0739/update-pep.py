import os
import pathlib
import shutil
import subprocess
import sys


def main() -> None:
    pep_dir = pathlib.Path(__file__).parent
    pep = pep_dir.parent / "pep-0739.rst"
    pep_bak = pep.with_name(pep.name + ".bak")
    schema = pep_dir / "python-build-info-v1.schema.json"
    schema_to_rst_script = pep_dir / "json-schema-to-rst.py"

    shutil.copy2(pep, pep_bak)
    try:
        schema_rst = subprocess.check_output(
            [
                sys.executable,
                os.fspath(schema_to_rst_script),
                os.fspath(schema),
                "-",
            ]
        ).decode()
        start_text, rest = pep.read_text().split(".. _spec-start:", maxsplit=1)
        end_text = rest.split(".. _spec-end:", maxsplit=1)[-1]
        pep.write_text(
            start_text
            + ".. _spec-start:\n\n"
            + schema_rst
            + "\n.. _spec-end:"
            + end_text
        )
    except:
        shutil.copy2(pep_bak, pep)
        raise


main()
