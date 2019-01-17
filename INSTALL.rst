.. _install:

DebOps installation
===================

DebOps can be installed in different ways depending on your requirements.  If
you plan to use only a subset of specific DebOps roles in your own
infrastructure, you can install the role repository from Ansible Galaxy. For
full functionality you should install the ``debops`` Python package, which lets
you configure and manage multiple project directories and provides easy way to
extend the DebOps roles if needed.

.. contents:: Sections
   :local:
   :depth: 2


Ansible Controller host
-----------------------

DebOps is designed to use Ansible in a "push" model, where Ansible commands are
executed on remote hosts from a central machine, the "Ansible Controller". This
host can use any OS that Ansible is supported on - Linux, macOS, Windows with
the `Windows Subsystem for Linux`__, etc. Use of an OS that can be managed
using DebOps (Debian, Ubuntu) might be preferable in the long run, however.

.. __: https://www.jeffgeerling.com/blog/2017/using-ansible-through-windows-10s-subsystem-linux

DebOps doesn't use any active services on the Ansible Controller host in the
infrastructure that is managed, therefore you might consider a laptop or
a virtual machine which can be turned off or put offline when not in use, for
better security. You should consider usage of an encrypted filesystem for
DebOps project directories due to sensitive nature of some of the data stored
in the :file:`secret/` directory, like :ref:`passwords <debops.secret>`,
:ref:`Certificate Authority <debops.pki>` files, etc.


Installation from Ansible Galaxy
--------------------------------

.. note:: This functionality is fully supported since DebOps v0.8.1+.

DebOps is available on `Ansible Galaxy`__, a central database of Ansible roles.
The project is `published there as a multi-repo`__, with Ansible roles and
playbooks available in one package. To install it on your Ansible Controller,
you have to use the `Mazer`__ content manager.

The ``debops`` Python package, described in the next section, contains its own
copy of DebOps roles and playbooks. If you want to go that route, you don't
need to install them from the Ansible Galaxy separately.

.. __: https://galaxy.ansible.com/
.. __: https://galaxy.ansible.com/debops/debops
.. __: https://galaxy.ansible.com/docs/mazer/index.html

After `installing Mazer using your preferred method`__, you can download the
DebOps repository by issuing the command:

.. __: https://galaxy.ansible.com/docs/mazer/install.html

.. code-block:: console

   mazer install debops.debops

The DebOps roles will be available in the directory:

.. code-block:: none

   ~/.ansible/content/debops/debops/roles/

To use them in your Ansible playbooks, you should add the path to the roles in
:file:`ansible.cfg` configuration file:

.. code-block:: ini

   [defaults]
   roles_path = $HOME/.ansible/content/debops/debops/roles:/etc/ansible/roles

Read the `documentation about using Mazer content in Playbooks`__ for more
details and examples.

.. __: https://galaxy.ansible.com/docs/mazer/examples.html#using-mazer-content

Upgrading an existing installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade the existing DebOps installation to the latest release published on
Ansible Galaxy, you can run the command:

.. code-block:: console

   mazer install --force debops.debops


Installation using a Python package
-----------------------------------

The `debops Python package`__ includes the DebOps roles and playbooks of
a given release, as well as a custom Python module which provides additional
functionality in DebOps roles, for example a way to override files and
templates without the need to modify the roles, or a way to "inject" additional
tasks into specific roles. You can also use a set of scripts which let you
create new "project directories" for your environments and execute DebOps
playbooks in a convenient way.

.. __: https://pypi.org/project/debops/

Ansible is an optional dependency of the ``debops`` Python package. This allows
you to use your own Ansible installation (either in a different Python
environment, or from OS packages) with DebOps.

Some of the DebOps roles require optional Python modules not required by
Ansible. You can install them using your distribution packages on Debian or
Ubuntu by running the command:

.. code-block:: console

   sudo apt install python-future python-ldap python-netaddr \
                    python-dnspython python-passlib

The missing Python dependencies will be automatically installed with the
``ansible`` and ``debops`` Python packages, however some of them, like the
``python-ldap`` package, are distributed only as sources and require the build
environment to be available. On Debian or Ubuntu you can install the required
packages by running the command:

.. code-block:: console

   sudo apt install build-essential python-dev libffi-dev libssl-dev \
                    libsasl2-dev libldap2-dev

Next, install DebOps and Ansible on your user account, from PyPI:

.. code-block:: console

   pip install --user debops[ansible]

The above command will install the ``debops`` Python package, as well as
``ansible`` Python package with optional dependencies used by DebOps roles.
They will be installed in the :file:`~/.local/lib/python2.7/site-packages/`
directory, the scripts and other binaries will be installed in
:file:`~/.local/bin` directory which should be included in your ``$PATH``.

To install only the ``debops`` Python package, without additional dependencies,
you can use the command:

.. code-block:: console

   pip install --user debops

In this case you will have to install Ansible and other optional dependencies
required by DebOps separately.


Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Some of the DebOps roles may depend on additional software installed on the
Ansible Controller. Some of these packages are available by default, the rest
can usually be installed using a system package manager.

Ansible
^^^^^^^

Current, stable Ansible release is required to run DebOps playbooks and roles.
Older Ansible releases may work for a time, but support for them is not
guaranteed by the project.

Ansible can be `installed in a variety of methods`__, you can choose your
preferred one depending on the platform you use for the Ansible Controller.
There are some caveats on specific platforms, described below.

.. __: https://docs.ansible.com/ansible/latest/intro_installation.html

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
  The :ref:`debops.pki` role requires Bash 4.x on the Ansible Controller for
  the management of the internal Certificate Authority. On macOS, you might
  need to upgrade an existing Bash 3.x installation before using DebOps.


Additional Python modules
^^^^^^^^^^^^^^^^^^^^^^^^^

`dnspython`__
  This is a Python library that provides various functions related to DNS
  queries. Some of the DebOps roles rely on DNS records to get information
  about the environment, like addresses of centralized services provided via
  DNS SRV records. In Ansible, this library is required by the ``dig`` lookup
  plugin.

.. __: http://www.dnspython.org/

`python-ldap`__
  This is a Python library which can be used to interface with the LDAP
  servers, Ansible `ldap_attr`__ and `ldap_entry`__ modules use it. You will
  need to install it if you want to manage LDAP using DebOps roles. It's
  available as ``python-ldap`` APT package in Debian, it can also be installed
  via PyPI.

.. __: https://www.python-ldap.org/en/latest/
.. __: https://docs.ansible.com/ansible/latest/ldap_attr_module.html
.. __: https://docs.ansible.com/ansible/latest/ldap_entry_module.html

`future`__
  This module provides a compatibility layer between Python 2.7 and Python 3.x
  versions. It allows creation of code that can be run in both old and new
  Python environments without changes.

.. __: http://python-future.org/

`netaddr`__
  This is a Python library which can be used to manipulate IP addresses in
  different ways. It's used by the ``ipaddr()`` Ansible filter plugin used in
  some of the DebOps roles. On Debian, it's available in the
  :command:`python-netaddr` APT packages, it can also be installed via PyPI.

.. __: https://github.com/drkjam/netaddr/

`passlib`__
  This is a Python library which is used by Ansible ``password()`` lookup
  plugin to encrypt passwords on Ansible Controller. This is required in DebOps
  roles that use :ref:`debops.secret` role to generate random passwords and
  store them in the :file:`secret/` directory. The library is available on
  Debian as the ``python-passlib`` APT package, it can also be installed via
  PyPI.

.. __: https://bitbucket.org/ecollins/passlib/wiki/Home

Additional, useful software
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
  other confidental data while not in use, for example in a :command:`git`
  repository.

.. __: https://en.wikipedia.org/wiki/EncFS

``uuidgen``
  This command is used to generate unique UUID strings for hosts which are then
  stored as Ansible facts. On Debian, it's available in the ``uuid-runtime``
  package.

Upgrading existing DebOps installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``debops`` Python package can be upgraded to the latest release using the
command:

.. code-block:: console

   pip install --user --upgrade debops

Installation of the development release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``debops`` Python package includes a :command:`debops-update` script which
can be used to install the DebOps monorepo directly from GitHub, with the
``master`` branch checked out by default. If you run this script without any
arguments, the repository will be installed in:

.. code-block:: none

   ~/.local/share/debops/debops/

Running the :command:`debops-update` again will refresh the repository.

If you specify a directory as an argument to the :command:`debops-update`
command, the monorepo will be cloned into the :file:`debops/` subdirectory of
that directory. This can be used to install the development version in
a specific DebOps project directory, for testing new releases:

.. code-block:: console

   debops-init ~/src/projects/test-env
   debops-update ~/src/projects/test-env

The monorepo installed in the :file:`debops/` subdirectory of a given DebOps
project directory will take precedence over the one installed globally in
:file:`~/.local/share/debops/debops/` or included in the Python package.
