.. _debops.python:

debops.python
=============

`Python`__ is a popular, dynamic programming language available on GNU/Linux
platforms. Ansible is written in Python and requires Python on remote host for
normal operations.

.. __: https://www.python.org/

The ``debops.python`` Ansible role can be used to manage the Python environment
on a Debian/Ubuntu host. Role supports multiple Python versions installed on
a host at the same time, which is the default practice in Debian.

A special "raw" mode of operation with a separate Ansible playbook can be used
to bootstrap Python environment on a host, so that Ansible can then install
packages and operate normally.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.python/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
