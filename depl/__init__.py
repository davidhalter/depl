"""
depl - deploy easy and fast.
Deploying stuff is hard, managing nginx and postgres painful, why not the easy
way?

Usage:
  depl deploy [-c=<file>] [<host>..]
  depl -h | --help

Options:
  -c, --config=<file>   Deploy configuration file [default: .depl.yml]
"""

import docopt

__version__ = '0.0.1'


def main():
    args = docopt.docopt(__doc__, version=__version__)
    print args
