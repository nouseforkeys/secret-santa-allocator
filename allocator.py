"""
This script allocates secret santa recipients.
"""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class Pairing:
    """stores the names of the secret santa pairing"""
    santa: str
    recipient: str|None = None


def import_group(filepath: Path) -> list[Pairing]:
    """imports the names in the group file into a list of pairings"""
    pairings = []
    with open(filepath) as groupfile:
        for line in groupfile.readlines():
            pairings.append(Pairing(line.strip()))
    return pairings

print(import_group(Path('group_2024.txt')))

