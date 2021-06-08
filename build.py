"""Build script for Sphinx documentation"""

import argparse
from pathlib import Path

from sphinx.application import Sphinx


def create_parser():
    parser = argparse.ArgumentParser(description="Build PEP documents")
    # alternative builders:
    parser.add_argument("-l", "--check-links", action="store_true")

    # flags / options
    parser.add_argument("-f", "--fail-on-warning", action="store_true")
    parser.add_argument("-n", "--nitpicky", action="store_true")
    parser.add_argument("-j", "--jobs", type=int)

    # extra build steps
    parser.add_argument("-i", "--index-file", action="store_true")  # for PEP 0

    return parser.parse_args()


if __name__ == "__main__":
    args = create_parser()

    root_directory = Path(".").absolute()
    source_directory = root_directory
    build_directory = root_directory / "build"  # synchronise with deploy-gh-pages.yaml -> deploy step
    doctree_directory = build_directory / ".doctrees"

    # builder configuration
    sphinx_builder = "dirhtml"
    if args.check_links:
        sphinx_builder = "linkcheck"

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
    app.builder.copysource = False  # Prevent unneeded source copying - we link direct to GitHub
    app.build()
