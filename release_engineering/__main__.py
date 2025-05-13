from __future__ import annotations

import argparse

CMD_UPDATE_PEPS = 'update-peps'
CMD_RELEASE_CYCLE = 'release-cycle'

PARSER = argparse.ArgumentParser(allow_abbrev=False)
PARSER.add_argument('COMMAND', choices=[CMD_UPDATE_PEPS, CMD_RELEASE_CYCLE])

args = PARSER.parse_args()
if args.COMMAND == CMD_UPDATE_PEPS:
    from release_engineering.update_release_schedules import update_peps

    update_peps()
elif args.COMMAND == CMD_RELEASE_CYCLE:
    from pathlib import Path

    from release_engineering.generate_release_cycle import create_release_cycle

    Path('release-cycle.json').write_text(create_release_cycle(), encoding='utf-8')
