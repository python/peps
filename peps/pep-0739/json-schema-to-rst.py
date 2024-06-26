import argparse
import contextlib
import io
import json
import os
import pathlib
import sys
import textwrap
from typing import Iterator, Literal, Required, TypedDict


class SchemaObject(TypedDict):
    type: Required[Literal["object", "string", "number"]]
    description: str
    # object properties
    required: list[str]
    additionalProperties: bool
    properties: dict[str, "SchemaObject"]


class SchemaRenderer:
    def __init__(self, file: io.TextIOBase) -> None:
        self._file = file
        self._header_level = 0
        self._ident = 0

    @classmethod
    def render(cls, schema: SchemaObject, output: io.TextIOBase) -> None:
        renderer = cls(output)
        renderer.write_schema(schema)

    def write_line(self, *lines: str | None) -> None:
        # print(f'write_line({lines})', file=sys.stderr)
        if not lines:
            lines = [None]
        for line in lines:
            if line is None:
                line = ""
            ident_prefix = self._ident * " "
            self._file.write(ident_prefix + line + "\n")

    def write_text(self, text: str) -> None:
        self.write_line(*textwrap.wrap(text, width=80), None)

    def write_wrapped_text(
        self,
        text: str,
        initial_prefix: str,
        subsequent_prefix: str | None = None,
        *,
        width: int = 80,
    ) -> None:
        if subsequent_prefix is None:
            subsequent_prefix = initial_prefix
        assert len(initial_prefix) == len(subsequent_prefix)
        if not text:
            self.write_line()
            return
        lines = text.splitlines()
        first_line = lines[0]
        # don't wrap literals
        if first_line.lstrip(" *-").startswith("``"):
            self.write_line(initial_prefix + first_line)
        else:
            wrapped_first_line = textwrap.wrap(
                first_line,
                width=width - len(initial_prefix),
                initial_indent=initial_prefix,
                subsequent_indent=subsequent_prefix,
                break_long_words=False,
                break_on_hyphens=False,
            )
            self.write_line(*wrapped_first_line)
        for line in lines[1:]:
            self.write_wrapped_text(line, initial_prefix=subsequent_prefix)

    def write_list_item(self, name: str, *items: str | list[str]) -> None:
        # write header
        ident = "    "
        prefix = ident + "* - "
        self.write_wrapped_text(name, prefix, " " * len(prefix))
        # write items
        for item in items:
            prefix = ident + "  - "
            if isinstance(item, list):
                self.write_wrapped_text(
                    "\n".join(f"- {entry}" for entry in item), prefix, " " * len(prefix)
                )
            else:
                self.write_wrapped_text(item, prefix, " " * len(prefix))

    @contextlib.contextmanager
    def write_header(self, title: str) -> Iterator[None]:
        header_characters = ["-", "~", "+", "_"]
        self.write_line(title, header_characters[self._header_level] * len(title), None)
        self._header_level += 1
        assert self._header_level <= len(
            header_characters
        ), "Not enough header character types"
        yield
        self._header_level -= 1

    def write_object_info(  # noqa: C901
        self, obj: SchemaObject, *, required: bool | None = None
    ) -> None:
        self.write_line(".. list-table::", "    :widths: 25 75", None)
        # schema
        for item in ("$schema", "$id"):
            if item in obj:
                self.write_list_item(f"``{item}``", obj[item])
        if "title" in obj:
            self.write_list_item("Title", obj["title"])
        # type
        type_ = obj["type"]
        type_description = f"``{type_}``"
        if "const" in obj:
            const = obj["const"]
            type_description += f" (constant — ``{const}``)"
        if "enum" in obj:
            enum_str = ", ".join(f"``{entry}``" for entry in obj["enum"])
            type_description += f" (enum — {enum_str})"
        self.write_list_item("Type", type_description)
        # description
        if "description" in obj:
            self.write_list_item("Description", obj["description"])
        # examples
        if "examples" in obj:
            examples = obj["examples"]
            examples_reprs = [f"``{example}``" for example in examples] + ["etc."]
            # if the examples are long, display them in a list
            if any(len(repr) >= 16 for repr in examples_reprs):
                self.write_list_item("Examples", examples_reprs)
            else:
                self.write_list_item("Examples", ", ".join(examples_reprs))
        # required
        if required is not None:
            self.write_list_item("Required", f"**{required!s}**")
        # object-specific info
        if obj["type"] == "object":
            # additional properties
            additional_properties = obj.get("additionalProperties", True)
            additional_properties_string = (
                "Allowed" if additional_properties else "Not allowed"
            )
            self.write_list_item(
                "Additional properties", f"**{additional_properties_string}**"
            )
        # separator line
        self.write_line()

    def write_object_properties(
        self, obj: SchemaObject, *, parent: str | None = None
    ) -> None:
        if "properties" not in obj:
            return
        required_properties = obj.get("required", [])
        for name, data in obj["properties"].items():
            full_name = f"{parent}.{name}" if parent else name
            with self.write_header(f"``{full_name}``"):
                self.write_object(
                    data, parent=full_name, required=name in required_properties
                )

    def write_object(
        self,
        obj: SchemaObject,
        *,
        parent: str | None = None,
        required: bool | None = None,
    ) -> None:
        self.write_object_info(obj, required=required)
        if obj["type"] == "object":
            self.write_object_properties(obj, parent=parent)

    def write_schema(self, schema: SchemaObject) -> None:
        assert "title" in schema
        self.write_object(schema)


def error(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", type=pathlib.Path)
    parser.add_argument("output", type=str, nargs="?")
    parser.add_argument("--overwrite", "-f", action="store_true")

    args = parser.parse_args()

    if not args.schema.is_file():
        error(f"{os.fspath(args.schema)} is not a file.")

    if not args.output:
        for suffix in (".schema.json", ".json"):
            if args.schema.name.endswith(suffix):
                name = args.schema.name.removesuffix(suffix)
                break
        else:
            name = args.schema.name
        args.output = args.schema.with_name(name + ".rst")

    with args.schema.open() as f:
        schema_data = json.load(f)

    if args.output == "-":
        SchemaRenderer.render(schema_data, sys.stdout)
    else:
        output = pathlib.Path(args.output)
        if output.is_file() and not args.overwrite:
            error(
                f"{os.fspath(output)} already exists, pass --overwrite/-f to overwrite it."
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w") as f:
            SchemaRenderer.render(schema_data, f)


main()
