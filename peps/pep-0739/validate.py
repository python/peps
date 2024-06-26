import json
import pathlib

import jsonschema


def main() -> None:
    pep_dir = pathlib.Path(__file__).parent
    schema = pep_dir / "python-build-info-v1.schema.json"
    example = pep_dir / "example.json"

    with schema.open() as f:
        schema_data = json.load(f)
    with example.open() as f:
        example_data = json.load(f)

    jsonschema.validate(example_data, schema_data)


main()
