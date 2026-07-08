from __future__ import annotations

import argparse

commands = (
    CMD_FULL_JSON := 'full-json',
    CMD_UPDATE_PEPS := 'update-peps',
    CMD_RELEASE_CYCLE := 'release-cycle',
    CMD_CALENDAR := 'calendar',
)
parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('COMMAND', choices=commands)

args = parser.parse_args()
if args.COMMAND == CMD_UPDATE_PEPS:
    from release_management.update_release_schedules import update_peps

    raise SystemExit(update_peps())

if args.COMMAND == CMD_FULL_JSON:
    from release_management import ROOT_DIR
    from release_management.serialize import create_release_json

    json_path = ROOT_DIR / 'python-releases.json'
    json_path.write_text(create_release_json(), encoding='utf-8')
    raise SystemExit(0)

if args.COMMAND == CMD_RELEASE_CYCLE:
    from release_management import ROOT_DIR
    from release_management.serialize import create_release_cycle

    json_path = ROOT_DIR / 'release-cycle.json'
    json_path.write_text(create_release_cycle(), encoding='utf-8')
    raise SystemExit(0)

if args.COMMAND == CMD_CALENDAR:
    from release_management import ROOT_DIR
    from release_management.serialize import create_release_schedule_calendar

    calendar_path = ROOT_DIR / 'release-schedule.ics'
    calendar_path.write_text(create_release_schedule_calendar(), encoding='utf-8')
    raise SystemExit(0)
