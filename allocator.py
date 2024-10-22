"""
This script allocates secret santa recipients.
"""

import argparse
from dataclasses import dataclass
import logging
from pathlib import Path
from random import shuffle, seed
from time import time

LOGGER = logging.getLogger(Path(__file__).name)


class AllocationError(ValueError):
    """custom error for if something goes wrong with the allocating"""


@dataclass
class Pairing:
    """stores the names of the secret santa pairing"""
    santa: str
    recipient: str | None = None

    def to_textfile(self, folder: Path, message: str) -> None:
        """
        Creates a textfile for the pairing. Keywords SANTA and RECIPIENT are
        replaced with this pairing's values
        """
        filename = folder / f'{self.santa}.txt'
        file_message = message\
            .replace('SANTA', self.santa).\
            replace('RECIPIENT', self.recipient)
        with open(filename, 'w') as textfile:
            textfile.write(file_message + '\n')
        LOGGER.debug(f'Created "{filename}" with text: "{file_message}"')

    def check(self) -> None:
        """raises an exception if this pair's santa and recipient match"""
        if self.santa == self.recipient:
            raise AllocationError(f'Someone got themselves! {self}')


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
    '-m', '--message-file',
    default=None,
    help=f'{Pairing.to_textfile.__doc__}'
)
parser.add_argument(
    '-s', '--seed',
    default=None,
    help='Seed value for random shuffle. '
    'Leave unspecified to just use the time',
)
parser.add_argument(
    '-d', '--debug-logs',
    action='store_true',
    help='Set to enable debug level logs (You\'ll see all the allocations so '
    'don\'t use when allocating for real!)'
)
args = parser.parse_args()

if args.debug_logs:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

group_file = Path(args.group)
pairings = import_group(group_file)

if args.seed is None:
    time_seed = time()
    seed(time_seed)
    LOGGER.info(f'Random seed using time: {time_seed}')
else:
    seed(args.seed)
    LOGGER.info(f'Random seed using specified value: {args.seed}')


LOGGER.info('He\'s making a list...')
remaining = [pair.santa for pair in pairings]
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


LOGGER.info('...And checking it twice!')
for _ in range(2):
    for pair in pairings:
        pair.check()


if args.message_file is None:
    message = 'RECIPIENT'
    LOGGER.info('Default message loaded')
else:
    with open(Path(args.message_file)) as msgfile:
        message = msgfile.read().strip()
    LOGGER.info(f'Message from "{args.message_file}" loaded')

output_folder = Path(group_file.stem)
output_folder.mkdir(exist_ok=True)
LOGGER.info(f'Saving outputs to: "./{output_folder}/"')

for pair in pairings:
    pair.to_textfile(output_folder, message)

LOGGER.info(f'{len(pairings)} files created. Merry Christmas!!')
