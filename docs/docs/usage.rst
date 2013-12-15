Usage
=====

``depl.yml`` files
------------------

The most important thing in your depl application is that you create a depl.yml
file that contains at least your deploy settings, e.g. deploying Django could
look like

.. sourcecode:: yaml

    deploy:
        - django:
            settings: settings.prod

On the command line you can use ``depl deploy myserver.com`` to deploy your
project. You can also add your ``myserver.com`` :ref:`to your settings
<hosts>`.

There is extensive documentation for all supported :ref:`Web Frameworks
<web-frameworks>` and :ref:`Services <services>`.


Command Line Options
--------------------

Generally the command line interface looks like this::

    Usage:
      depl (deploy|remove) [-c=<file>] [-p=<file>] [<host>...]
      depl run [-c=<file>] [-p=<file>] <command> [<host>...]
      depl -h | --help

    Options:
      -c, --config=<file>   Deploy configuration file [default: depl.yml]
      -p, --pool=<name>     Define a pool that is going to be deployed.

Only the ``deploy`` and ``run`` commands are working. The ``remove`` command is
already reserverd.

.. _hosts:

Hosts / Pools
-------------

While it's possible to easily define hosts (so you don't always have to use
them while using ``depl deploy myhost.com``):

.. sourcecode:: yaml

    deploy:
        - redis
    hosts:
        - myhost.com:
            password: "the answer is 42"
        - host_with_key.com  # it is always prefered to use keys.

It's also possible to group hosts with pools:

.. sourcecode:: yaml

    deploy:
        - postgresql
        - django:
            port: 8080
    hosts:
        - databases.com
            password: "pg rocks"
        - i_dont_like_long_urls.myhost.webservers.com
            id: webservers

    pools:
        db:
            deploy: [postgresql]
            hosts: [databases.com]
        web:
            deploy: [django]
            hosts: [webservers]

I'm not sure if anybody is ever going to use that, though.


Extend other depl modules
-------------------------

Just use the extends identifier::

    deploy:
        - redis
    extends:
        - foo.yml
        - bar.yml

Files are automatically merged - it works like multiple inheritance.


Custom Scripts
--------------

There's two ways of writing custom scripts within depl. The first one is ``sh``
, a simple shell script (which shell depends currently on fabric_):

.. sourcecode:: yaml

    deploy:
        - sh: |
            echo "Hello World"

The second one would be ``fab``. Fab basically resembles the fab files of
fabric_. It's writing Python with an ``from fabric.api import *`` in front.
This is also the way how depl scripts work internally:

.. sourcecode:: yaml

    deploy:
        - fab: |
            with warn_only():
                sudo('echo "Hello World"')


.. _fabric: https://github.com/fabric/fabric
