.. include:: global.rst

depl - deploying should be easy
===============================

Release v\ |release|. (:doc:`Installation <docs/installation>`)

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


.. _toc:

Docs
----

.. toctree::
   :maxdepth: 2

   docs/installation
   docs/usage
   docs/web-frameworks
   docs/services
   docs/plugin-api
   docs/development


.. _resources:

Resources
---------

- `Source Code on Github <https://github.com/davidhalter/depl>`_
- `Travis Testing <https://travis-ci.org/davidhalter/depl>`_
- `Python Package Index <http://pypi.python.org/pypi/depl/>`_
- `Test Coverage <https://coveralls.io/r/davidhalter/depl>`_
