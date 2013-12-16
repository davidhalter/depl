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

Documentation
-------------

If you want to know more in general, just read the documentation at
`<http://depl.rtfd.org>`_!


Support
-------

Currently depl supports Ubuntu/Debian (apt-get), the others:

- Arch Linux (pacman) could be implemented
- Fedora/CentOS/RHEL (rpm) could be implemented
- Windows/Apple: Discussions needed (but probably not?!).

Depl is written in Python. Python 3 support will be ready once fabric_ supports
Python 3.


Additional Ideas
----------------

- DNS configuration
- Central logging
- High Availability tools like HAProxy to make it easy not to go offline for a
  few seconds while deploying.
- Could generate e.g. an ansible_ recipe with depl. Possible?
- Write a "depl server" with different backends (e.g. amazon clouds) to
  automate the process of deploying and increasing servers.
- Add support for automatic travis testing with depl files. Is that even
  possible?

Contributing
------------

Read `CONTRIBUTING.md
<https://github.com/davidhalter/jedi/blob/master/CONTRIBUTING.md>`_ to check
how you can contribute! There's also a small developer documentation `available
<depl.readthedocs.org/en/latest/docs/development.html#testing>`_.


Testing
-------

Use a virtual machine for testing, please. `Why?
<depl.readthedocs.org/en/latest/docs/development.html#testing>`_

.. _article: http://jedidjah.ch/code/2013/10/
.. _ansible: https://github.com/ansible/ansible
.. _fabric: https://github.com/fabric/fabric
