.. include:: global.rst

depl - deploying should be easy
===============================

Release v\ |release|. (:doc:`Installation <docs/installation>`)

Deploying stuff is hard, managing nginx and postgres painful, why don't we
solve that problem? Simple deployments should not involve tweaking
configurations, that you have never dealt with before. ``depl`` solves this.

Let's deploy Django to a live server! Create a file called ``depl.yml``::
    
    deploy:
        - django:
            port: 0  # 0 to disable
            settings: settings_prod
            ssl:
                key: /path/to/key
                certificate: /path/to/cert
    hosts:
        - myhost.com

And run ``depl deploy`` in that same directory. After this two step process
your website will be running on ``https://myhost.com``. It only works on Ubuntu
servers for now (maybe also Debian), but will work on other systems in the
future as well.

This will connect to ``myhost.com`` by SSH, install all necessary software
packages and initialize your project. For the Django example this would involve
installing ``nginx``, ``uwsgi``, ``postgresql`` (if required by Django's
``settings.py``), install all Python dependencies and run on your production
settings.

Currently this is also working for `Meteor
<depl.readthedocs.org/en/latest/docs/web-frameworks.html#meteor>`_ and 
`WSGI <depl.readthedocs.org/en/latest/docs/development.html#testing>_` (which
includes flask).


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
