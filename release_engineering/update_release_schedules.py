"""Update release schedules in PEPs.

The ``python-releases.toml`` data is treated as authoritative for the given
versions in ``VERSIONS_TO_REGENERATE``. Each PEP must contain markers for the
start and end of each release schedule (feature, bugfix, and security, as
appropriate). These are:

    .. feature release schedule
    .. bugfix release schedule
    .. security release schedule
    .. end of schedule

This script will use the dates in the [[release."{version}"]] tables to create
and update the release schedule lists in each PEP.

Optionally, to add a comment or note to a particular release, use the ``note``
field, which will append the given text in brackets to the relevant line.

Usage:

    $ python -m release_engineering update-peps
    $ # or
    $ make regen-all
"""

from __future__ import annotations

import datetime as dt

from release_engineering import (
    PEP_ROOT,
    ReleaseInfo,
    VersionMetadata,
    load_python_releases,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator

    from release_engineering import ReleaseSchedules, ReleaseState, VersionMetadata

TODAY = dt.date.today()

VERSIONS_TO_REGENERATE = (
    '3.8',
    '3.9',
    '3.10',
    '3.11',
    '3.12',
    '3.13',
    '3.14',
)


def update_peps() -> None:
    python_releases = load_python_releases()
    for version in VERSIONS_TO_REGENERATE:
        metadata = python_releases.metadata[version]
        schedules = create_schedules(
            version,
            python_releases.releases[version],
            metadata.start_of_development,
            metadata.end_of_bugfix,
        )
        update_pep(metadata, schedules)


def create_schedules(
    version: str,
    releases: list[ReleaseInfo],
    start_of_development: dt.date,
    bugfix_ends: dt.date,
) -> ReleaseSchedules:
    schedules: ReleaseSchedules = {
        ('feature', 'actual'): [],
        ('feature', 'expected'): [],
        ('bugfix', 'actual'): [],
        ('bugfix', 'expected'): [],
        ('security', 'actual'): [],
    }

    # first entry into the dictionary
    db_state: ReleaseState = 'actual' if TODAY >= start_of_development else 'expected'
    schedules['feature', db_state].append(
        ReleaseInfo(
            stage=f'{version} development begins',
            state=db_state,
            date=start_of_development,
        )
    )

    for release_info in releases:
        if release_info.stage.startswith(f'{version}.0'):
            schedules['feature', release_info.state].append(release_info)
        elif release_info.date <= bugfix_ends:
            schedules['bugfix', release_info.state].append(release_info)
        else:
            assert release_info.state == 'actual', release_info
            schedules['security', release_info.state].append(release_info)

    return schedules


def update_pep(metadata: VersionMetadata, schedules: ReleaseSchedules) -> None:
    pep_path = PEP_ROOT.joinpath(f'pep-{metadata.pep:0>4}.rst')
    pep_lines = iter(pep_path.read_text(encoding='utf-8').splitlines())
    output_lines: list[str] = []
    schedule_name = ''
    for line in pep_lines:
        output_lines.append(line)
        if line.startswith('.. ') and 'schedule' in line:
            schedule_name = line.split()[1]
            assert schedule_name in {'feature', 'bugfix', 'security'}
            output_lines += generate_schedule_lists(
                schedules,
                schedule_name=schedule_name,
                feature_freeze_date=metadata.feature_freeze,
            )

            # skip source lines until the end of schedule marker
            while True:
                line = next(pep_lines, None)
                if line == '.. end of schedule':
                    output_lines.append(line)
                    break
                if line is None:
                    raise ValueError('No end of schedule marker found!')

    if not schedule_name:
        raise ValueError('No schedule markers found!')

    with open(pep_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
        f.write('\n')  # trailing newline


def generate_schedule_lists(
    schedules: ReleaseSchedules,
    *,
    schedule_name: str,
    feature_freeze_date: dt.date = dt.date.min,
) -> Iterator[str]:
    state: ReleaseState
    for state in 'actual', 'expected':
        if not schedules.get((schedule_name, state)):
            continue

        yield ''
        if schedule_name != 'security':
            yield f'{state.title()}:'
            yield ''
        for release_info in schedules[schedule_name, state]:
            yield release_info.schedule_bullet
            if release_info.note:
                yield f'  ({release_info.note})'
            if release_info.date == feature_freeze_date:
                yield '  (No new features beyond this point.)'

    if schedule_name == 'bugfix':
        yield '  (final regular bugfix release with binary installers)'

    yield ''


if __name__ == '__main__':
    update_peps()
