.. _install:

DebOps installation
===================

This section of the documentation describes how to install all of the
components needed to run DebOps playbooks.


Ansible Controller
------------------

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


Ansible
-------

Current, stable Ansible release is required to run DebOps playbooks and roles.
Older Ansible releases may work for a time, but support for them is not
guaranteed by the project.

Ansible can be `installed in a variety of methods`__, you can choose your
preferred one depending on the platform you use for the Ansible Controller.
There are some caveats on specific platforms, described below.

.. __: https://docs.ansible.com/ansible/latest/intro_installation.html

Debian
  On Debian Stretch, you can use the :command:`ansible` package from the
  ``stretch-backports`` repository; Ansible version included in the Stretch
  release is not sufficient anymore.

  On older Debian releases, you should consider installing Ansible by creating
  a ``.deb`` package from the official :command:`git` repository sources. You
  can find a :command:`bootstrap-ansible` script which can do this for you
  automatically in the :ref:`debops.ansible` Ansible role :file:`files/`
  subdirectory.

macOS
  The ``debops`` Python package which contains scripts and modules used by the
  project is currently available only through `PyPI`__. Due to this, Ansible
  installed using `Homebrew`__ might not work correctly with DebOps playbooks
  and/or roles. In that case, you should install Ansible from PyPI.

  The :ref:`debops.pki` role requires Bash 4.x on the Ansible Controller for
  the management of the internal Certificate Authority. On macOS, you might
  need to upgrade an existing Bash 3.x installation before using DebOps.

  .. __: https://pypi.python.org/
  .. __: https://brew.sh/


Additional software
-------------------

Some of the DebOps roles may depend on additional software installed on the
Ansible Controller. Some of these packages are available by default, the rest
can usually be installed using a system package manager.

`EncFS`__
  The :command:`encfs` command is used to manage an encrypted user-space
  filesystem which holds the contents of the :file:`secret/` directory. This is
  an optional feature, useful if you want to protect your secrets at rest.

.. __: https://en.wikipedia.org/wiki/EncFS

`git`__
  The :command:`git` tool is used to manage DebOps monorepo installation or
  updates by the :command:`debops-update` command.

.. __: https://git-scm.com/

`gpg`__
  The :command:`gpg` command is used by the :command:`debops-padlock` script to
  encrypt and decrypt files with EncFS passphrase. It's usually already
  installed by the operating system.

.. __: https://www.gnupg.org/

`python-dnspython`__
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

`python-netaddr`__
  This is a Python library which can be used to manipulate IP addresses in
  different ways. It's used by the ``ipaddr()`` Ansible filter plugin used in
  some of the DebOps roles. On Debian, it's available in the
  :command:`python-netaddr` APT packages, it can also be installed via PyPI.

.. __: https://github.com/drkjam/netaddr/

`python-passlib`__
  This is a Python library which is used by Ansible ``password()`` lookup
  plugin to encrypt passwords on Ansible Controller. This is required in DebOps
  roles that use :ref:`debops.secret` role to generate random passwords and
  store them in the :file:`secret/` directory. The library is available on
  Debian as the ``python-passlib`` APT package, it can also be installed via
  PyPI.

.. __: https://bitbucket.org/ecollins/passlib/wiki/Home

``uuidgen``
  This command is used to generate unique UUID strings for hosts which are then
  stored as Ansible facts. On Debian, it's available in the ``uuid-runtime``
  package.


DebOps scripts
--------------

The DebOps scripts are `available via PyPI`__, to install them on the Ansible
Controller you can use the command:

.. code-block:: console

   sudo pip install debops

An upgrade is also possible with the command:

.. code-block:: console

   sudo pip install --upgrade debops

.. __: https://pypi.python.org/pypi/debops

At the moment installation on an unprivileged user account doesn't work as
expected, system-wide installation should work fine.

DebOps monorepo
---------------

If you installed DebOps using a Python package equal or newer than ``0.7.0``,
the installation should include a set of DebOps playbooks and roles located in
the ``debops`` Python package directory. The scripts should automatically find
them and use them as necessary.

If you installed an older DebOps release, or you want to use the latest changes
in DebOps development branch, you can use the :command:`debops-update` command
to download or update the DebOps monorepo. The :command:`git` repository will
be cloned to the directory:

.. code-block:: console

   ~/.local/share/debops/debops/

You can also execute the command:

.. code-block:: console

   debops-update <path-to-directory>

This will clone the repository to the :file:`debops/` subdirectory inside of
the specified directory. This allows you to create a "local" copy of the DebOps
monorepo which will be used by the :command:`debops` script instead of the
user-wide repository.

Running the :command:`debops-update` command will update the existing DebOps
monorepo, either the user-wide clone, or the one found in a local directory.


Installation in a Python virtualenv
-----------------------------------

You can install Ansible and DebOps in a `Python virtualenv`__ environment.
These instructions are for Debian Jessie or Debian Stretch, they should also
work in Ubuntu.

.. __: https://virtualenv.pypa.io/en/stable/

First install python virtual-env packages and other system dependencies
required for building:

.. code-block:: console

   sudo apt-get install python-virtualenv virtualenv build-essential \
                        python-dev libffi-dev libssl-dev libsasl2-dev \
                        libldap2-dev


Next we activate the DebOps virtual environment and prepare it for use:

.. code-block:: console

   virtualenv debops-venv
   cd debops-venv
   source bin/activate
   pip install --upgrade setuptools
   pip install ansible debops

After DebOps is installed, you might want to create symlinks to the
:command:`debops` scripts in :file:`/usr/local/bin/` directory to make the
commands available outside of the the Python virtual environment:

.. code-block:: console

   ln -s debops-venv/bin/ansible          /usr/local/bin/ansible
   ln -s debops-venv/bin/ansible-playbook /usr/local/bin/ansible-playbook
   ln -s debops-venv/bin/debops           /usr/local/bin/debops
   ln -s debops-venv/bin/debops-init      /usr/local/bin/debops-init
   ln -s debops-venv/bin/debops-update    /usr/local/bin/debops-update
   ln -s debops-venv/bin/debops-defaults  /usr/local/bin/debops-defaults

If your Ansible/DebOps-Controller machine has SElinux enabled, delegating tasks
to ``localhost`` is problematic. `A workaround for this issue`__ is to add
a definition for ``localhost`` to your inventory, outside of the
``[debops_all_hosts]`` inventory group:

.. __: https://dmsimard.com/2016/01/08/selinux-python-virtualenv-chroot-and-ansible-dont-play-nice/

.. code-block:: none

   localhost ansible_python_interpreter=/usr/bin/python

This makes Ansible use the SElinux libraries from the python-environment
*outside* of the virtualenv.
