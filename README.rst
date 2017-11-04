DebOps
======

|DebOps logo|

*Your Debian-based data center in a box*

|CII Best Practices| |Travis-CI|

.. |DebOps logo| image:: https://raw.githubusercontent.com/debops/debops/master/lib/images/debops-small.png
   :target: https://debops.org/

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/237/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/237

.. |Travis-CI| image:: https://img.shields.io/travis/debops/debops.svg?style=flat
   :target: https://travis-ci.org/debops/debops


The DebOps project provides a set of general-purpose `Ansible <https://github.com/ansible/ansible/>`__
roles that can be used to manage `Debian <https://www.debian.org/>`__ or
`Ubuntu <https://www.ubuntu.com>`__ hosts. In addition, a default set of
Ansible playbooks can be used to apply the provided roles in a controlled way,
using Ansible inventory groups.

The roles are written with a high customization in mind, which can be done
using Ansible inventory. This way the role and playbook code can be shared
between multiple environments, with different configuration in to each one.

Services can be managed on a single host, or spread between multiple hosts.
DebOps provides support for different SQL and NoSQL databases, web servers,
programming languages and specialized applications useful in a data center
environment or in a cluster. The project can also be used to deploy
virtualization environments using KVM/libvirt, Docker or LXC technologies to
manage virtual machines and/or containers.

You can find out more about DebOps features on the
`project's documentation page <https://docs.debops.org/>`__.


Installation
------------

DebOps requires a Python 2.7 environment and Ansiible 2.3+ to work correctly.
Read the `INSTALL.rst <https://github.com/debops/debops/blob/master/INSTALL.rst>`__
file for specific installation instructions.


Getting started
---------------

Ansible uses SSH to connect to and manage the hosts. DebOps enforces the SSH
security by disabling password authentication, therefore using SSH keys to
connect to the hosts is strongly recommended. This can be changed using the
inventory variables.

During initial deployments you might find that the firewall created by DebOps
blocked you from accessing the hosts. Because of that it's advisable to have an
out-of-band console access to the host which can be used to login and
troubleshoot the connection.

Create a new environment within a DebOps "project directory", add some hosts in
the Ansible inventory and run the default DebOps playbook against them to
configure them:

.. code-block:: console

   # Create a new environment
   debops-init ~/src/projects/my-environment
   cd ~/src/projects/my-environment

   # Modify the 'ansible/inventory/hosts' file to suit your needs, for example
   # uncomment the local host to configure it with DebOps

   # Run the full playbook against all hosts in the inventory
   debops

   # Run the common playbook against specific host in the inventory
   debops common -l <hostname>

You should read the `Getting Started with DebOps <https://docs.debops.org/en/latest/debops-playbooks/docs/guides/getting-started.html>`_
guide for a more in-depth explanation of how the project can be used to manage
multiple hosts via Ansible.


Development
-----------

Create `a fork of this repository <https://github.com/debops/debops/fork>`_ and
clone it to your workstation. Create a development DebOps environment and
symlink the forked repository in it. Now you can create new playbooks/roles in
the forked repository and see their results in the development environment.

.. code-block:: console

   git clone git@github.com:<username>/debops ~/src/github.com/<username>/debops
   cd ~/src/github.com/<username>/debops
   git remote add upstream https://github.com/debops/debops.git

   debops-init ~/src/projects/debops-devel
   cd ~/src/projects/debops-devel
   ln -s ~/src/github.com/<username>/debops debops

You can pull latest changes to the project from the upstream repository:

.. code-block:: console

   cd ~/src/github.com/<username>/debops
   git checkout master
   git fetch upstream
   git rebase upstream/master

Read the `DEVELOPMENT.rst <https://github.com/debops/debops/blob/master/DEVELOPMENT.rst>`__
file for more details about the DebOps development process.


Contributing
------------

DebOps development is done via a distributed model. New features and changes
are prepared in a `fork of the official repository <https://github.com/debops/debops/fork>`_
and are published to the original repository via GitHub pull requests. PRs are
reviewed by the DebOps developer team and if accepted, are merged in the main
repository.

GPG-signed ``git`` commits are preferred to ensure authenticity.

Read the `CONTRIBUTING.rst <https://github.com/debops/debops/blob/master/CONTRIBUTING.rst>`__
file for more details about how to contribute to DebOps.


Licensing
---------

The DebOps project is licensed under the `GNU Gneral Public License 3.0 <https://www.gnu.org/licenses/gpl-3.0>`__.
You can find full text of the license in the `LICENSE <https://github.com/debops/debops/blob/master/LICENSE>`__ file.
