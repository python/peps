from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

TYPE_CHECKING = False
if TYPE_CHECKING:
    import datetime as dt
    from typing import Literal, TypeAlias

    ReleaseState: TypeAlias = Literal['actual', 'expected']
    ReleaseSchedules: TypeAlias = dict[tuple[str, ReleaseState], list['ReleaseInfo']]
    VersionStatus: TypeAlias = Literal[
        'feature', 'prerelease', 'bugfix', 'security', 'end-of-life'
    ]

RELEASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = RELEASE_DIR.parent
PEP_ROOT = ROOT_DIR / 'peps'
_PYTHON_RELEASES = None

dc_kw = {'kw_only': True, 'slots': True} if sys.version_info[:2] >= (3, 10) else {}


@dataclass(frozen=True, **dc_kw)
class PythonReleases:
    metadata: dict[str, VersionMetadata]
    releases: dict[str, list[ReleaseInfo]]


@dataclass(frozen=True, **dc_kw)
class VersionMetadata:
    """Metadata for a given interpreter version (MAJOR.MINOR)."""

    pep: int
    status: VersionStatus
    branch: str
    release_manager: str
    start_of_development: dt.date
    feature_freeze: dt.date
    first_release: dt.date
    end_of_bugfix: dt.date  # a.k.a. security mode or source-only releases
    end_of_life: dt.date

    @classmethod
    def from_toml(cls, data: dict[str, int | str | dt.date]):
        return cls(**{k.replace('-', '_'): v for k, v in data.items()})


@dataclass(frozen=True, **dc_kw)
class ReleaseInfo:
    """Information about a release."""

    stage: str
    state: ReleaseState
    date: dt.date
    note: str = ''  # optional note / comment, displayed in the schedule

    @property
    def schedule_bullet(self):
        """Return a formatted bullet point for the schedule list."""
        return f'- {self.stage}: {self.date:%A, %Y-%m-%d}'


def load_python_releases() -> PythonReleases:
    global _PYTHON_RELEASES
    if _PYTHON_RELEASES is not None:
        return _PYTHON_RELEASES

    with open(RELEASE_DIR / 'python-releases.toml', 'rb') as f:
        python_releases = tomllib.load(f)
    all_metadata = {
        v: VersionMetadata.from_toml(metadata)
        for v, metadata in python_releases['metadata'].items()
    }
    all_releases = {
        v: [ReleaseInfo(**r) for r in releases]
        for v, releases in python_releases['release'].items()
    }
    _PYTHON_RELEASES = PythonReleases(metadata=all_metadata, releases=all_releases)
    return _PYTHON_RELEASES
