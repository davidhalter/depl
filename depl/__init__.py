"""
depl - deploy easy and fast.
Deploying stuff is hard, managing nginx and postgres painful, why not the easy
way?

Usage:
  depl deploy [-c=<file>] [<host>...]
  depl run [-c=<file>] <command> [<host>...]
  depl -h | --help

Options:
  -c, --config=<file>   Deploy configuration file [default: .depl.yml]
"""

import docopt
from config import Config

__version__ = '0.0.1'


def main():
    args = docopt.docopt(__doc__, version=__version__)
    c = Config(args['--config'], args['<host>'])
    if args['deploy']:
        pass
    elif args['run']:
        run('depl run ')
