DebOps
======

|DebOps logo|

> Your Debian-based data center in a box

|CII Best Practices| |Travis-CI|

.. |DebOps logo| image:: https://raw.githubusercontent.com/debops/debops/master/lib/images/debops-small.png
   :target: https://debops.org/

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/237/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/237

.. |Travis-CI| image:: https://img.shields.io/travis/debops/debops.svg?style=flat
   :target: https://travis-ci.org/debops/debops

DebOps is a collection of `Ansible <https://github.com/ansible/ansible/>`__
roles and playbooks designed to configure `Debian <https://www.debian.org/>`__
or `Ubuntu <https://www.ubuntu.com>`__ hosts in a production environment. The
project can configure most of the supported services on a single host, or
create and manage a cluster of hosts with encrypted communication between the
nodes.

Installation
------------

DebOps requires a Python 2.7 environment and Ansiible 2.4+ to work correctly.
See the :file:`INSTALL.rst` file for specific installation instructions.

In the future, this repository will contain all of the DebOps roles, playbooks
and other code. In the meantime if you are looking for it, check the
`debops-tools <https://github.com/debops/debops-tools/>`_ and
`debops-playbooks <https://github.com/debops/debops-playbooks/>`_ repositories.

Why merge the repositories
--------------------------

The reasons and discussion about merging the repositories can be found on the
DebOps mailing list, you can read the
`initial post <https://lists.debops.org/pipermail/debops-users/2017-August/000078.html>`_
and check `the whole thread <https://lists.debops.org/pipermail/debops-users/2017-August/thread.html>`_
for discussion.

Status of the merge
-------------------

The current status of the merge can be tracked on the `GitHub project page <https://github.com/debops/debops/projects/1>`_.
