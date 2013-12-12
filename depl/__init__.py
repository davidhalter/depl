"""
depl - deploy easy and fast.
Deploying stuff is hard, managing nginx and postgres painful, why not the easy
way?

Usage:
  depl deploy [-c=<file>] [-p=<file>] [<host>...]
  depl run [-c=<file>] [-p=<file>] <command> [<host>...]
  depl -h | --help

Options:
  -c, --config=<file>   Deploy configuration file [default: depl.yml]
  -p, --pool=<name>     Define a pool that is going to be deployed.
"""

import sys

import docopt

from depl import config
from depl import hosts

__version__ = '0.0.1'


def main():
    args = docopt.docopt(__doc__, version=__version__)
    try:
        c = config.Config(args['--config'], args['<host>'], args['--pool'])
    except IOError:
        sys.stderr.write("Couldn't find config file.")
        sys.exit(1)
    except config.ValidationError as e:
        sys.stderr.write("Config file is invalid: " + e.message)
        sys.exit(2)

    for pool in c.pools:
        if args['deploy']:
            hosts.execute_pool(pool, 'deploy')
        elif args['run']:
            hosts.run_in_pool([args['<command>']])
