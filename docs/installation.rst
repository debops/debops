Installation
============

DebOps scripts are distributed on `PyPI`_, Python Package Index. They can be
installed using the ``pip`` command::

    pip install debops

You can also use ``pip`` to upgrade the scripts themselves::

    pip install --upgrade debops

After the installation is finished, scripts will be available in
``/usr/local/bin/``, which should be in your shell's ``$PATH``.

.. _PyPI: https://pypi.python.org/pypi/

DebOps prerequisites
--------------------

To use DebOps playbooks, you need some additional tools on your Ansible
Controller besides the official scripts. Some of these tools will be installed
for you by ``pip`` as prerequisites of the scripts.

Ansible
  You need to install Ansible to use DebOps playbooks. DebOps is developed and
  used on current development version of Ansible, however we try not to use
  certain features until they are available in current stable release.

Python ``netaddr`` library
  This is a Python library used to manipulate strings containing IP addresses
  and networks. DebOps provides an Ansible plugin (included in Ansible 1.9+)
  which uses this library to manipulate IP addresses.

  You can install ``netaddr`` either using your favourite package manager, or
  through ``pip``.

Python ``ldap`` library
  This Python library is used to access and manipulate LDAP servers. It can be
  installed through your package manager or using ``pip``.

``uuidgen``
  This command is used to generate unique identifiers for hosts which are then
  saved as Ansible facts and can be used to identify hosts in the playbook. In
  most Linux or MacOSX desktop distributions this command should be already
  installed. If not, it can be usually found in the ``uuid-runtime`` package.

``encfs``
  This is an optional application, which is used by the ``debops-padlock``
  script to encrypt the ``secret/`` directory within DebOps project
  directories, which holds confidential data like passwords, private keys and
  certificates. EncFS is available on Linux distributions, usually as the
  ``encfs`` package.

``gpg``
  GnuPG is used to encrypt the file which holds EncFS password; this allows you
  to share the encrypted ``secret/`` directory with other users without sharing
  the password, and using private GPG keys instead. ``debops`` script will
  automatically decrypt the keyfile and use it to open an EncFS volume.

  GnuPG is usually installed on Linux or MacOSX operating systems.

