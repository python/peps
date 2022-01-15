"""Build script for Sphinx documentation"""

import argparse
from pathlib import Path

from sphinx.application import Sphinx


def create_parser():
    parser = argparse.ArgumentParser(description="Build PEP documents")
    # alternative builders:
    builders = parser.add_mutually_exclusive_group()
    builders.add_argument("-l", "--check-links", action="store_const",
                          dest="builder", const="linkcheck",
                          help='Check validity of links within PEP sources. '
                               'Cannot be used with "-f" or "-d".')
    builders.add_argument("-f", "--build-files", action="store_const",
                          dest="builder", const="html",
                          help='Render PEPs to "pep-NNNN.html" files (default). '
                               'Cannot be used with "-d" or "-l".')
    builders.add_argument("-d", "--build-dirs", action="store_const",
                          dest="builder", const="dirhtml",
                          help='Render PEPs to "index.html" files within "pep-NNNN" directories. '
                               'Cannot be used with "-f" or "-l".')

    # flags / options
    parser.add_argument("-w", "--fail-on-warning", action="store_true",
                        help="Fail the Sphinx build on any warning.")
    parser.add_argument("-n", "--nitpicky", action="store_true",
                        help="Run Sphinx in 'nitpicky' mode, "
                             "warning on every missing reference target.")
    parser.add_argument("-j", "--jobs", type=int, default=1,
                        help="How many parallel jobs to run (if supported). "
                             "Integer, default 1.")

    return parser.parse_args()


def create_index_file(html_root: Path, builder: str) -> None:
    """Copies PEP 0 to the root index.html so that /peps/ works."""
    pep_zero_file = "pep-0000.html" if builder == "html" else "pep-0000/index.html"
    try:
        pep_zero_text = html_root.joinpath(pep_zero_file).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    if builder == "dirhtml":
        pep_zero_text = pep_zero_text.replace('="../', '="')  # remove relative directory links
    html_root.joinpath("index.html").write_text(pep_zero_text, encoding="utf-8")


if __name__ == "__main__":
    args = create_parser()

    root_directory = Path(".").absolute()
    source_directory = root_directory
    build_directory = root_directory / "build"  # synchronise with deploy-gh-pages.yaml -> deploy step
    doctree_directory = build_directory / ".doctrees"

    # builder configuration
    if args.builder is not None:
        sphinx_builder = args.builder
    else:
        # default builder
        sphinx_builder = "html"

    # other configuration
    config_overrides = {}
    if args.nitpicky:
        config_overrides["nitpicky"] = True

    app = Sphinx(
        source_directory,
        confdir=source_directory,
        outdir=build_directory,
        doctreedir=doctree_directory,
        buildername=sphinx_builder,
        confoverrides=config_overrides,
        warningiserror=args.fail_on_warning,
        parallel=args.jobs,
    )
    app.build()

    create_index_file(build_directory, sphinx_builder)
