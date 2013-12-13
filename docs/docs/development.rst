depl Development
================

.. note:: This documentation is for depl developers who want to improve depl
    itself, but have no idea how depl works.


Introduction
------------

``depl`` is currently a very small program, so it should still be very easy to
understand if you read the code. depl is built on fabric_ and there's no way to
change things without knowing a little bit about fabric. If you happen to know
fabric most depl code is really easy to understand.

The only thing that really deserves to be mentioned is the internal
configuration verifier. There's a grammar file called ``grammar.yml``, that is
being compared to your own project-based ``depl.yml`` file. This grammar file
compares all the types and if raises an error if something is wrongly
formatted.


.. _testing:

Testing
-------

We heavily rely on pytest_ for testing. Testing ``depl`` correctly involves a
lot of integration tests. Therefore I recommend you to use a virtual machine
for testing. Alternatively you can just create a pull request, which travis
automatically tests.

``depl`` will open a lot of ports and testing might even create security holes
on your computer - so really - use a VM.

You can run tests like this::

    sudo pip install tox
    sudo aptitude install libpq-dev python-dev

    tox

The goal is to keep at least 90% testing coverage.


Contributing
------------

See `CONTRIBUTING.md
<https://github.com/davidhalter/jedi/blob/master/CONTRIBUTING.md>`_.

.. _fabric: https://github.com/fabric/fabric
.. _pytest: http://pytest.org/latest/
