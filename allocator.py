"""
This script allocates secret santa recipients.
"""

import argparse
from dataclasses import dataclass
import logging
from pathlib import Path
from random import shuffle, seed
from time import time

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@dataclass
class Pairing:
    """stores the names of the secret santa pairing"""
    santa: str
    recipient: str | None = None


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


parser = argparse.ArgumentParser(
    prog='Secret santa allocator',
    description=__doc__,
    epilog='Merry Christmas!',
)
parser.add_argument(
    'group',
    help='Text file with people\'s names. Delimit with newlines.'
)
parser.add_argument(
    '-s', '--seed',
    default=None,
    help='sSed value for random shuffle. '
    'Leave unspecified to just use the time',
)
args = parser.parse_args()

pairings = import_group(args.group)

if args.seed is None:
    time_seed = time()
    seed(time_seed)
    LOGGER.info(f'random seed using time: {time_seed}')
else:
    seed(args.seed)
    LOGGER.info(f'random seed using specified value: {args.seed}')

LOGGER.info('Allocating pairs...')
remaining = [pair.santa for pair in pairings]
# allocate a recipient to each santa
for pair in pairings:
    LOGGER.debug(f'Allocating for: {pair.santa}')
    # create a list of remaining recipients without the santa
    options = [name for name in remaining if pair.santa != name]
    LOGGER.debug(f'{options=}')

    # if on the penultimate allocation we need to do something different
    # we need to make sure that the last person isn't given themselves
    # so when we get here if one of the options is the last person then we
    # must force this to be the penultimate allocation so we don't get stuck
    if (len(options) == 2) and (pairings[-1].santa in options):
        pair.recipient = pairings[-1].santa
        LOGGER.debug('Forced allocation to avoid getting stuck')
    else:
        # shuffle it and pick one of the names
        shuffle(options)
        pair.recipient = options.pop()
        LOGGER.debug('Randomly allocated recipient')

    LOGGER.debug(f'{pair=}')
    # remove the recipient from the remaining names
    remaining.remove(pair.recipient)
