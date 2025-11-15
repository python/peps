from __future__ import annotations

import dataclasses
import json
import re

from icalendar import Calendar, Event

from release_management import load_python_releases

TYPE_CHECKING = False
if TYPE_CHECKING:
    from release_management import VersionMetadata


def create_release_json() -> str:
    python_releases = dataclasses.asdict(load_python_releases())
    return json.dumps(
        python_releases,
        indent=2,
        sort_keys=False,
        ensure_ascii=False,
        default=str,
    )


def create_release_cycle() -> str:
    metadata = load_python_releases().metadata
    all_versions = sorted(
        ((d.first_release, v) for v, d in metadata.items()), reverse=True
    )
    versions = [v for _date, v in all_versions if version_to_tuple(v) >= (2, 6)]
    release_cycle = {version: version_info(metadata[version]) for version in versions}
    rc_json = json.dumps(release_cycle, indent=2, sort_keys=False, ensure_ascii=False)
    return f'{rc_json}\n'


def version_to_tuple(version: str, /) -> tuple[int, ...]:
    return tuple(map(int, version.split('.')))


def version_info(metadata: VersionMetadata, /) -> dict[str, str | int]:
    end_of_life = metadata.end_of_life.isoformat()
    if metadata.status != 'end-of-life':
        end_of_life = end_of_life.removesuffix('-01')
    return {
        'branch': metadata.branch,
        'pep': metadata.pep,
        'status': metadata.status,
        'first_release': metadata.first_release.isoformat(),
        'end_of_life': end_of_life,
        'release_manager': metadata.release_manager,
    }


def ical_uid(name: str) -> str:
    user = re.sub(r'[^a-z0-9.]+', '', name.lower())
    return f'python-{user}@python.org'


def create_release_ical() -> str:
    python_releases = load_python_releases()

    calendar = Calendar()
    calendar.add('version', '2.0')
    calendar.add('prodid', '-//Python Software Foundation//Python releases//EN')
    calendar.add('x-wr-calname', 'Python releases')
    calendar.add(
        'x-wr-caldesc', 'Python releases schedule from https://peps.python.org'
    )

    all_releases = []
    for version, releases in python_releases.releases.items():
        for release in releases:
            all_releases.append((version, release))

    all_releases.sort(key=lambda r: r[1].date)

    for version, release in all_releases:
        event = Event()
        event.add('summary', f'Python {release.stage}')
        event.add('uid', ical_uid(release.stage))
        event.add('dtstart', release.date)
        pep_number = python_releases.metadata[version].pep
        event.add('url', f'https://peps.python.org/pep-{pep_number:04d}/')

        if release.note:
            event.add('description', f'Note: {release.note}')

        calendar.add_component(event)

    return calendar.to_ical().decode('utf-8')
