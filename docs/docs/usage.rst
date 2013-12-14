Usage
=====

The most important thing in your 

Hosts / Pools
-------------

While it's possible to easily define hosts (so you don't always have to use
them while using ``depl deploy myhost.com``)::

    deploy:
        - redis
    hosts:
        - myhost.com:
            password: "the answer is 42"
        - host_with_key.com  # it is always prefered to use keys.

It's also possible to group hosts with pools::

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
, a simple shell script (which shell depends currently on fabric_)::

    deploy:
        - sh: |
            echo "Hello World"

The second one would be ``fab``. Fab basically resembles the fab files of
fabric_. It's writing Python with an ``from fabric.api import *`` in front.
This is also the way how depl scripts work internally::

    deploy:
        - fab: |
            with warn_only():
                sudo('echo "Hello World"')


.. _fabric: https://github.com/fabric/fabric
