from __future__ import annotations

import json

from release_engineering import load_python_releases

TYPE_CHECKING = False
if TYPE_CHECKING:
    from release_engineering import VersionMetadata


def create_release_cycle() -> str:
    metadata = load_python_releases().metadata
    versions = [v for v in metadata if version_to_tuple(v) >= (2, 6)]
    versions.sort(key=version_to_tuple, reverse=True)
    if '2.7' in versions:
        versions.remove('2.7')
        versions.insert(versions.index('3.1'), '2.7')

    release_cycle = {version: version_info(metadata[version]) for version in versions}
    return (
        json.dumps(release_cycle, indent=2, sort_keys=False, ensure_ascii=False) + '\n'
    )


def version_to_tuple(version: str, /) -> tuple[int, ...]:
    return tuple(map(int, version.split('.')))


def version_info(metadata: VersionMetadata, /) -> dict[str, str]:
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
