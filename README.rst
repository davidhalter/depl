depl - deploying should be easy
===============================

.. image:: https://secure.travis-ci.org/davidhalter/depl.png?branch=master
    :target: http://travis-ci.org/davidhalter/depl
    :alt: Travis-CI build status

.. image:: https://coveralls.io/repos/davidhalter/depl/badge.png?branch=master
    :target: https://coveralls.io/r/davidhalter/depl
    :alt: Coverage Status

.. image:: https://pypip.in/d/depl/badge.png
    :target: https://crate.io/packages/depl/
    :alt: Number of PyPI downloads

.. image:: https://pypip.in/v/depl/badge.png
    :target: https://crate.io/packages/depl/
    :alt: Latest PyPI version


**DON'T LOOK DON'T PUBLISH. please don't!**


Why do we need another deploy tool?
-----------------------------------

Read `this article I wrote <article>`_!


What depl does not, yet.
------------------------

- No DNS configuration
- No central logging
- No High Availability tools like HAProxy

A lot of web-frameworks and tools have yet to be supported.

Support
-------

Current supports Ubuntu/Debian (apt-get), others:

- Arch Linux (pacman) could be implemented
- Fedora/CentOS/RHEL (rpm) could be implemented
- Windows/Apple: Discussions needed (but probably not?!).

Python 3 support will be ready once fabric_ supports Python 3.


Additional Ideas
----------------

- Could generate e.g. an ansible_ recipe with depl. Possible?
- Write a "depl server" with different backends (e.g. amazon clouds) to
  automate the process of deploying and increasing servers.
- Add support for automatic travis testing with depl files. Is that even
  possible?

Contributing
------------

Read `CONTRIBUTING.md
<https://github.com/davidhalter/jedi/blob/master/CONTRIBUTING.md>`_ to see how
you can contribute! There's also a small developer documentation `available
<depl.readthedocs.org/en/latest/docs/development.html#testing>`_.


Testing
-------

Use a virtual machine for testing, please. `Why?
<depl.readthedocs.org/en/latest/docs/development.html#testing>`_

.. _article: http://jedidjah.ch/code/2013/10/
.. _ansible: https://github.com/ansible/ansible
.. _fabric: https://github.com/fabric/fabric
