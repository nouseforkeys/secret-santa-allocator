"""
This script allocates secret santa recipients.
"""

from dataclasses import dataclass
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@dataclass
class Pairing:
    """stores the names of the secret santa pairing"""
    santa: str
    recipient: str|None = None


def import_group(filepath: Path) -> list[Pairing]:
    """imports the names in the group file into a list of pairings"""
    pairings = []
    LOGGER.info(f'Importing from file: "{filepath}"')
    with open(filepath) as groupfile:
        for line in groupfile.readlines():
            pairings.append(Pairing(line.strip()))
    LOGGER.info(f'Imported {len(pairings)} names')
    LOGGER.debug(f'{pairings=}')
    return pairings

pairings = import_group('group_2024.txt')
