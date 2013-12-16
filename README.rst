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


``depl`` is a pre-alpha prototype. **We want to start a discussion about how
developers deploy. How can we improve the current situation?** Please tell us
why you think depl is not the right tool for you! Tell us what you think needs
to be changed! We hope to make small and medium deployments easy.

Deploying stuff is hard, managing nginx and postgres painful. Why don't we
solve that problem? Simple deployments should not involve tweaking
configurations that you have never dealt with before. ``depl`` solves this.

Let's `deploy Django
<depl.readthedocs.org/en/latest/docs/web-frameworks.html#meteor>`_ to a live
server! Create a file called ``depl.yml``::
    
    deploy:
        - django:
            settings: settings_prod
            ssl:
                key: /path/to/key
                certificate: /path/to/cert
    hosts:
        - myhost.com

And run ``depl deploy`` in that same directory. After this two step process
your website will be running on ``https://myhost.com`` and
``http://myhost.com``. It only works on Ubuntu servers for now (maybe also
Debian), but will work on other systems in the future as well.

``depl`` would connect to ``myhost.com`` by SSH, install all necessary software
packages and initialize your project. In our Django example this would involve
installing ``nginx``, ``uwsgi``, ``postgresql`` (if required by Django's
``settings.py``). It would install all Python dependencies and run on your
production settings.

Currently this is also working for `Meteor
<depl.readthedocs.org/en/latest/docs/web-frameworks.html#meteor>`_ and 
`WSGI <depl.readthedocs.org/en/latest/docs/development.html#testing>`_ (which
includes flask).

Why depl and not ansible, puppet, chef, docker or vagrant?
----------------------------------------------------------

Have you ever tried those tools? ansible, puppet and chef are really
complicated to understand. They are made for big deployments, for large scale
operation engineers. You can read the blog posts below, they explain a bit
more. Generally depl solves the use case for all small deployments on your own
server, those tools do something different.

Docker and Vagrant are completely different tools. They make controlling VMs
easy. They do not install your software. However, depl could be used in
combination with either of them.

Blog Posts talking about depl
-----------------------------

- `The current state of deploying Django applications
  <http://jedidjah.ch/code/2013/12/16/django-deployment/>`_!
- `Platform as a Service: A Market Analysis
  <http://jedidjah.ch/code/2013/12/16/paas/>`_!


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
