Introduction
============

``debops.secret`` role enables you to have a separate directory on the Ansible
Controller (different than the playbook directory and inventory directory)
which can be used as a handy "workspace" for other roles.

Some usage examples of this role in `DebOps`_ include:

- password lookups, either from current role, or using known location of
  passwords from other roles, usually dependencies (for example
  ``debops.mariadb`` role can manage an user account in the database with
  random password and other role can lookup that password to include in
  a generated configuration file);

- secure file storage, for example for application keys generated on remote
  hosts (``debops.boxbackup`` role retrieves client keys for backup
  purposes), for that reason secret directory should be protected by an
  external means, for example encrypted filesystem (currently there is no
  encryption provided by default);

- secure workspace (``debops.boxbackup`` role, again, uses the secret directory
  to create and manage Root CA for backup servers – client and server
  certificates are automatically downloaded to Ansible Controller, signed and
  uploaded to destination hosts);

- simple centralized backup (specific roles like ``debops.sshd``,
  ``debops.pki`` and ``debops.monkeysphere`` have separate task lists that
  are invoked by custom playbooks to allow backup and restoration of ssh host
  keys and SSL certificates. Generated .tar.gz files are kept on Ansible
  Controller in secret directory).

.. _DebOps: https://debops.org/


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.secret

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
