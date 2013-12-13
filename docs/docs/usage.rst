Usage
=====

.. automodule:: depl

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
