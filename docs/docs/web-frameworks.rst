.. include:: ../global.rst

.. _web-frameworks:

Web Frameworks
==============

Currently we support the following frameworks/languages:

- :ref:`Django <django>`
- :ref:`Meteor <meteor>`
- :ref:`Python WSGI & Flask & others... <wsgi>`

Support for Rails, Java, Scala  and whatever else is hopefully coming soon! We
need experts, to tell us at least which tools we should use to deploy. So if
you want to see your web framework, just join open an issue_ and start a
discussion!


.. _general-web:

General Web Options & SSL
-------------------------

All are web frameworks (at least until now) are using nginx as a reverse proxy.
This makes it possible to use a multitude of ports and frameworks on the same
server.

There's a general set of web options, basically every web host has these
options (read the grammar_ file!!!):
    
.. sourcecode:: yaml

    deploy:
        - meteor:
            url: localhost
            port: 80  # 0 to disable
            redirect: null  # 'https' to redirect to the https port

            ssl:
                port: 443  # to disable
                redirect: null  # 'http' to redirect to the http port
                certificate: null  # a file path
                key: null  # a file path

As you can see, there's a way to play with the ports and specify an url (to
host multiple domains on the same server). There's also a way to specify an ssl
key/certificate. By default if not specified, depl generates self-signed
certificates for you (obviously only working with a warning in the browser).
This makes it possible 

A typical django ssl configuration with ssh might look like this:

.. sourcecode:: yaml

    deploy:
        - django:
            redirect: https
            ssl:
                certificate: ~/.private/ssl/cert.crt
                key: ~/.private/ssl/ssl.key


.. _django:

Django
------

.. automodule:: depl.deploy.django


.. _meteor:

Meteor
------

.. automodule:: depl.deploy.meteor


.. _wsgi:

Python WSGI & Flask & others...
-------------------------------

.. automodule:: depl.deploy.wsgi
