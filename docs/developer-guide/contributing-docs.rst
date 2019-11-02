.. _contributing_docs:

Contributing to the Documentation
=================================

| Did you just have to trawl through source code to find out what something does?
| Did you have to ask someone on IRC?
| Have you just proudly accomplished your task despite the documentation's lack of relevant information?

Well, help us improve it!

Overview
--------

DebOps' documentation is written in `reStructuredText`__,
built with `Sphinx`__, hosted on readthedocs
and lives in the ``docs/`` folder of the `monorepo`__.

.. __: http://docutils.sourceforge.net/rst.html
.. __: https://www.sphinx-doc.org/
.. __: https://github.com/debops/debops/tree/master/docs

The documentation for roles lives in ``doc/ansible/roles/``.

You can build the documentation yourself on
:ref:`your local fork<contribution_workflow>` by running ``make docs`` from your
project folder. The resulting html files will be in ``docs/_build/html/``.

Documentation suggestions
-------------------------

These are a few subjects the current documentation is lacking.

User guide
~~~~~~~~~~

- **Debugging tips**: How to find and fix bugs in DebOps
- **The DebOps CLI**: Description of the debops commands
- **Script configuration**: Description of ``debops.cfg`` configuration options

Admin guide
~~~~~~~~~~~

- **Host Preparation**: Describe how DebOps hosts should be prepared (bootstrapped) for management
- **Common Configuration**: Describe default configuration applied on hosts by the common playbook
- **Basic virtualization**: Describe virtualization on a basic level with LXC, libvirt+KVM
- **Basic mail server**: Describe mail server setup with Postfix, Dovecot
- **Development network**: Describe Vagrant replacement, a development network with DNS, DHCP, PXE and preseeding

Developer guide
~~~~~~~~~~~~~~~

- **Monorepo layout**: How the DebOps github monorepo is structured
- **Code standards**: How to write Ansible roles for DebOps
- **Software sources**: How DebOps handles external software
- **Project roadmap**: Long term plans for DebOps

Tester guide
~~~~~~~~~~~~

- **Test methodology**: Describe how DebOps is tested
- **Travis CI tests**: How DebOps is tested on Travis CI
- **GitLab CI tests**: How DebOps is tested on GitLab CI
- **Vagrant documentation**: Information about Vagrant usage in tests
- **Jane documentation**: Information about Jane
- **Testinfra documentation**: Information about testinfra usage
