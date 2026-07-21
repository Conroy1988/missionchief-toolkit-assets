#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUT = ROOT / 'docs/issue-285-contribution-diagnostic.txt'


def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    start = source.find('function missionRequirementsUnitContribution')
    if start < 0:
        raise RuntimeError('unit contribution function not found')
    end = source.find('function missionRequirementsAggregate', start)
    if end < 0:
        end = source.find('function missionRequirementsCoverageRow', start)
    if end < 0:
        raise RuntimeError('unit contribution function end not found')
    OUT.write_text(source[start:end], encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
