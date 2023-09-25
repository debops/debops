.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Imre Jonk <mail@imrejonk.nl>
.. Copyright (C) 2019      Alin Alexandru <alin.alexandru@innobyte.com>
.. Copyright (C) 2017-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _install:

DebOps installation
===================

.. contents::
   :local:
   :depth: 2

.. include:: ../includes/global.rst


Installation types
------------------

DebOps can be installed in different ways depending on your needs:

- As a Python package in a Python environment of a given UNIX account.
  Different UNIX accounts can use their own versions of DebOps.

- As a Python package in a Python :command:`virtualenv` environment. A given
  UNIX account can use different versions of DebOps by switching to each
  :command:`virtualenv` environment.

- As an Ansible Collection installed from the Ansible Galaxy using the
  :command:`ansible-galaxy` command. This is a good solution if you are
  interested only in specific DebOps roles and you don't want to use the
  additional scripts to manage your environments.

In any case, the installation will be performed on a Linux, macOS or Windows
(WSL) computer which will be called the "Ansible Controller". This machine will
be used to execute Ansible commands against other, remote hosts which will be
managed using DebOps roles and playbooks.

DebOps doesn't use any active services on the Ansible Controller host in the
infrastructure that is managed, therefore you might consider a laptop or
a virtual machine which can be turned off or put offline when not in use, for
better security. You should consider using an encrypted filesystem for DebOps
project directories due to sensitive nature of some of the data stored in the
:file:`secret/` directory, like :ref:`passwords <debops.secret>`,
:ref:`Certificate Authority <debops.pki>` files, etc.


Installation in the UNIX account Python environment
---------------------------------------------------

The `debops Python package`__ includes the DebOps roles and playbooks of
a given release, as well as a custom Python module which provides additional
functionality in DebOps roles, for example a way to override files and
templates without the need to modify the roles, or a way to "inject" additional
tasks into specific roles. You can also use a set of scripts which let you
create new "project directories" for your environments and execute DebOps
playbooks in a convenient way.

.. __: https://pypi.org/project/debops/

Ansible is an optional installation dependency of the ``debops`` Python
package. This allows you to use your own Ansible installation (either in
a different Python environment, or from OS packages) with DebOps.

Required Python packages
~~~~~~~~~~~~~~~~~~~~~~~~

Some of the DebOps roles require optional Python modules not required by
Ansible:

`dnspython`__
  This is a Python library that provides various functions related to DNS
  queries. Some of the DebOps roles rely on DNS records to get information
  about the environment, like addresses of centralized services provided via
  DNS SRV records. In Ansible, this library is required by the ``dig`` lookup
  plugin.

.. __: http://www.dnspython.org/

`python-ldap`__
  This is a Python library which can be used to interface with the LDAP
  servers. The `Ansible community.general.ldap_attr module`_ and
  `Ansible community.general.ldap_entry module`_ use it. You will need to
  install it if you want to manage LDAP using DebOps roles. It's available as
  ``python-ldap`` APT package in Debian, it can also be installed via PyPI.

.. __: https://www.python-ldap.org/en/latest/

`future`__
  This module provides a compatibility layer between Python 2.7 and Python 3.x
  versions. It allows creation of code that can be run in both old and new
  Python environments without changes.

.. __: https://python-future.org/

`netaddr`__
  This is a Python library which can be used to manipulate IP addresses in
  different ways. It's used by the ``ipaddr()`` Ansible filter plugin used in
  some of the DebOps roles. On Debian, it's available in the
  :command:`python-netaddr` APT packages, it can also be installed via PyPI.

.. __: https://github.com/drkjam/netaddr/

`passlib`__
  This is a Python library which is used by the Ansible ``password()`` lookup
  plugin to encrypt passwords on the Ansible Controller. This is required in
  DebOps roles that use :ref:`debops.secret` role to generate random passwords
  and store them in the :file:`secret/` directory. The library is available on
  Debian as the ``python-passlib`` APT package, it can also be installed via
  PyPI.

.. __: https://passlib.readthedocs.io/en/stable/

`toml`__
  This is a Python library which is used by the DebOps custom Jinja filters
  ``from_toml`` and ``to_toml`` which are used by some roles that configure
  software using TOML as configuration data format.

.. __: https://github.com/uiri/toml

You can install them using your distribution packages on Debian or
Ubuntu by running the command:

.. code-block:: console

   sudo apt install python3-future python3-ldap python3-netaddr \
                    python3-dnspython python3-passlib python3-toml

The missing Python dependencies will be automatically installed with the
``ansible`` and ``debops`` Python packages, however some of them, like the
``python3-ldap`` package, are distributed only as sources and require the build
environment to be available. On Debian or Ubuntu you can install the required
packages by running the command:

.. code-block:: console

   sudo apt install build-essential python3-dev libffi-dev libssl-dev \
                    libsasl2-dev libldap2-dev python3-pip

Installation of DebOps with Ansible included
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install DebOps and Ansible on your user account, execute the command:

.. code-block:: console

   pip3 install --user debops[ansible]

The above command will install the ``debops`` Python package, as well as
``ansible`` Python package with optional dependencies used by DebOps roles.
They will be installed in the :file:`~/.local/lib/python3.x/site-packages/`
directory, the scripts and other binaries will be installed in
:file:`~/.local/bin` directory which should be included in your ``$PATH``.

.. note:: The ``debops`` Python package contains its own set of DebOps roles
          and playbooks, which can be accessed by the :command:`debops` script,
          you don't need to install the monorepo separately.

Installation of DebOps without Ansible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install only the ``debops`` Python package, without additional dependencies,
you can use the command:

.. code-block:: console

   pip3 install --user debops

In this case you will have to install Ansible and other optional dependencies
required by DebOps separately.

Ansible notes
~~~~~~~~~~~~~

The latest stable Ansible release is required to run DebOps playbooks and
roles. Older Ansible releases may work for a time, but support for them is not
guaranteed by the DebOps project.

Ansible can be `installed in a variety of methods`__, you can choose your
preferred one depending on the platform you use for the Ansible Controller.
There are some caveats on specific platforms, described below.

.. __: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

Debian
  On the current Debian Stable release, you might need to install the
  :command:`ansible` package from the Backports repository. DebOps development
  follows the stable Ansible releases, because of that the version of Ansible
  included in a Debian Stable release might not be sufficient anymore.

  If you want to, you can build your own Ansible ``.deb`` package from the
  :command:`git` source repository. The :ref:`debops.ansible` role contains
  a shell script, :command:`bootstrap-ansible`, which can be used to
  automatically build a Debian package suitable for DebOps.

macOS
  The :ref:`debops.pki` role requires Bash 4.x or higher on the Ansible
  Controller for the management of the internal Certificate Authority. On
  macOS, you might need to upgrade an existing Bash 3.x installation before
  using DebOps.


Additional, useful software
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`git`__
  The :command:`git` tool is used to manage DebOps monorepo installation or
  updates by the :command:`debops-update` command.

.. __: https://git-scm.com/

`gpg`__
  The :command:`gpg` command is used by the :command:`debops-padlock` script to
  encrypt and decrypt files with EncFS passphrase. It's usually already
  installed by the operating system.

.. __: https://www.gnupg.org/

`encfs`__
  The FUSE-based ``EncFS`` filesystem can be used to manage an encrypted volume
  which holds the contents of the :file:`secret/` directory. This is an optional
  feature, useful if you want to protect your passwords, X.509 certificates and
  other confidential data while not in use, for example in a :command:`git`
  repository.

.. __: https://en.wikipedia.org/wiki/EncFS

`git-crypt`__
  You can use :command:`git-crypt` to transparently encrypt files in the
  :file:`secret/` directory when committing to a Git repository. Unlike
  ``EncFS``, the files are not encrypted on your local hard disk, and the path
  names are not encrypted at all. The excellent 'Using git-crypt' section on
  the website or in the `man page`__ will get you started.

.. __: https://www.agwa.name/projects/git-crypt/
.. __: https://manpages.debian.org/git-crypt.1

``uuidgen``
  This command is used to generate unique UUID strings for hosts which are then
  stored as Ansible facts. On Debian, it's available in the ``uuid-runtime``
  package.

Upgrading existing DebOps installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``debops`` Python package can be upgraded to the latest release using the
command:

.. code-block:: console

   pip3 install --user --upgrade debops


Installation in a :command:`virtualenv` Python environment
----------------------------------------------------------

The installation of DebOps in a Python virtual environment is similar to
installation in the UNIX account Python environment. Importantly, some of the
Python packages required by DebOps are not distributed in a binary format and
require to be compiled. On Debian or Ubuntu, you have to install the required
development packages:

.. code-block:: console

   sudo apt install build-essential python3-virtualenv virtualenv python3-dev \
                    libffi-dev libssl-dev libsasl2-dev libldap2-dev python3-pip

After that, you can create a new Python :command:`virtualenv` environment in
a selected directory and "enter" it by executing the commands:

.. code-block:: console

   virtualenv ~/src/venv/debops
   cd ~/src/venv/debops
   source bin/activate

The current shell prompt will change to indicate that you are in a Python
virtual environment. Now, to install DebOps with Ansible included in the
environment, you can run the command:

.. code-block:: console

   pip3 install debops[ansible]

Or, to install only DebOps without Ansible (for example, you want to use the
Ansible from outside of the environment), you can execute the command:

.. code-block:: console

   pip3 install debops

To exit the current Python virtual environment, you can run the command:

.. code-block:: console

   deactivate

This will change your current shell prompt again, which will indicate that you
are now beyond the environment.

Upgrading existing :command:`virtualenv` Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the :command:`virtualenv` environment, you can upgrade to the latest release using the
command:

.. code-block:: console

   pip3 install --upgrade debops


Installation from Ansible Galaxy
--------------------------------

.. note:: This functionality is fully supported since DebOps v2.0.0+.

DebOps is available on `Ansible Galaxy`__, a central database of Ansible roles.
The project is `published there as a set of Ansible Collections`__, with
Ansible roles and playbooks split into multiple "packages" due to the number of
available roles. To install them on your Ansible Controller, you have to use
the :command:`ansible-galaxy` command provided with Ansible.

.. __: https://galaxy.ansible.com/
.. __: https://galaxy.ansible.com/debops/debops

To install the DebOps Collections, run the command:

.. code-block:: console

   ansible-galaxy collection install debops.debops

You can also install DebOps as a Collection directly from the monorepo using the command:

.. code-block:: console

   ansible-galaxy collection install git+https://github.com/debops/debops#/ansible/,master

This will install the collection from the ``master`` branch of the repository.
This form can also be used in the :file:`requirements.yml` file, like this:

.. code-block:: yaml

   ---
   collections:
     - name: 'git+https://github.com/debops/debops#/ansible/,master'

After saving the file, you can use the command:

.. code-block:: console

   ansible-galaxy install -r requirements.yml

to install the collection.

The DebOps Collections will be available in the directory:

.. code-block:: none

   ~/.ansible/collections/ansible_collections/debops/

The ``debops.debops`` Collection includes the playbooks provided with DebOps
which can be used to execute roles after setting up the required Ansible
inventory. Various roles that use custom lookup or filter plugins are modified
to use them from the Collections as well, but otherwise the roles should have
the same functionality as those included in the DebOps Python package or in the
monorepo.

Read the `documentation about using Ansible Collections in Playbooks`__ for
more details and examples.

.. __: https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#using-collections-in-a-playbook

Upgrading installed Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade the already installed DebOps Collections to the latest release
published on Ansible Galaxy, you can run the command:

.. code-block:: console

   ansible-galaxy collection install --force-with-deps debops.debops
