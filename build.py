# Build script for Sphinx documentation

import argparse
from pathlib import Path
from sphinx.application import Sphinx


def create_parser():

    parser = argparse.ArgumentParser(description="Build PEP documents")
    arguments = [
        ('-b', '--builder', 'store'),
        ('-d', '--dir-html', 'store_true'),
        ('-c', '--check-links', 'store_true'),
        ('-f', '--fail-on-warning', 'store_true'),
        ('-n', '--nitpicky', 'store_true'),
    ]
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], action=arg[2])

    return parser.parse_args()


if __name__ == '__main__':
    args = create_parser()

    root_directory = Path('.').absolute()
    source_directory = root_directory
    configuration_directory = source_directory
    build_directory = root_directory / 'build'
    doctree_directory = build_directory / '.doctrees'

    if args.check_links:
        builder = 'linkcheck'
    elif args.dir_html:
        builder = 'dirhtml'
    else:
        builder = 'html'

    config_overrides = {}
    if args.nitpicky:
        config_overrides['nitpicky'] = True

    app = Sphinx(
        source_directory, configuration_directory, build_directory, doctree_directory, builder,
        confoverrides=config_overrides, warningiserror=args.fail_on_warning,
    )
    app.builder.copysource = False  # Prevent unneeded source copying - we link direct to VCS
    app.build()
