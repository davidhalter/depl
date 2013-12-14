"""
depl - deploying should be easy.

Just create a `depl.yml` file in your project folder and specify your deploy
options. For more help how to create one, goto `depl.rtfd.org`. After that you
say `depl deploy` and you're done!

Usage:
  depl (deploy|remove) [-c=<file>] [-p=<file>] [<host>...]
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
        elif args['remove']:
            # no deploy tool has yet implemented that. To be discussed.
            raise NotImplementedError()
            hosts.execute_pool(pool, 'remove')
        elif args['run']:
            hosts.run_in_pool([args['<command>']])
