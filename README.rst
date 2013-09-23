depl - deploy easy and fast.
============================

**Please don't use this yet, it's in a planning phase.** Pretty soon I'm going
to start a discussion about it. Everything here is incomplete. The only reason
I'm already deploying is that I'm trying to prepare myself for a major
discussion about Python web deployment and deployment in general.

-------------------------------------------------------------------------------

Deploying is easy! For example create a ``.depl.yml`` file in your Django
project:

.. code:: yaml

    deploy:
        - django:  # you don't need the next lines, it does that automatically.
            url: subdomain.example.com
            after_script: echo "done!"
        - postgresql
        - reddis

And deploy to two different servers:

.. code:: bash

   depl deploy foo@example.com bar@example2.com


At the moment there are not a lot of configuration options, but the goal is to
make it possible to choose between different products (e.g.
``gunicorn``/``uwsgi`` or ``nginx``/``apache``). Support for different
languages/frameworks is also planned (``php``, ``ruby``, ``rails``, etc.).


Why do we need another deploy tool?
-----------------------------------

Read `this article I wrote <article>`_!


What depl does not
------------------

- No DNS configuration
- No central logging (yet?)


Support
-------

Current supports Ubuntu/Debian (apt-get), others:

- Arch Linux (pacman) could be implemented
- Fedora/CentOS/RHEL (rpm) could be implemented
- Windows/Apple: Discussions needed (but probably not?!).

Python 3 support will be ready once fabric_ supports Python 3.


Additional Ideas
----------------

- Add support for automatic travis conversions.

.. _article: http://jedidjah.ch/code/2013/10/
.. _fabric: https://github.com/fabric/fabric
