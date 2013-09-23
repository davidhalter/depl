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

import sys

import docopt

import config

__version__ = '0.0.1'


def main():
    args = docopt.docopt(__doc__, version=__version__)
    try:
        c = config.Config(args['--config'], args['<host>'])
    except IOError:
        sys.stderr.write("Couldn't find config file.")
        sys.exit(1)
    except config.ValidationError:
        sys.stderr.write("Config file is invalid.")
        sys.exit(2)
    if args['deploy']:
        pass
    elif args['run']:
        run('depl run')
