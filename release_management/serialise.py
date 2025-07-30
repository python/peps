from __future__ import annotations

import dataclasses
import json

from release_management import ROOT_DIR, load_python_releases

TYPE_CHECKING = False
if TYPE_CHECKING:
    from release_management import VersionMetadata


def create_release_json() -> str:
    python_releases = dataclasses.asdict(load_python_releases())
    return json.dumps(python_releases, indent=2, sort_keys=False, ensure_ascii=False, default=str)


def create_release_cycle() -> str:
    metadata = load_python_releases().metadata
    all_versions = sorted(
        ((d.first_release, v) for v, d in metadata.items()), reverse=True
    )
    versions = [v for _date, v in all_versions if version_to_tuple(v) >= (2, 6)]
    release_cycle = {version: version_info(metadata[version]) for version in versions}
    return (
        json.dumps(release_cycle, indent=2, sort_keys=False, ensure_ascii=False) + '\n'
    )


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
