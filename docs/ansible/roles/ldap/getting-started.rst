.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

.. include:: ../../../includes/global.rst


Ansible Controller requirements
-------------------------------

If you plan to use this role to perform LDAP tasks in the default
configuration, you need to install the ``python-ldap`` Python package in the
Ansible environment on the Controller host.

By default the role uses :command:`pass` (`Password Store`__) as a password
manager to store LDAP user credentials securely using GnuPG. As a fallback, you
can also provide the required password using an environment variable on the
Ansible Controller, or configure your own password lookup method.

.. __: https://www.passwordstore.org/


.. _ldap__ref_ldap_init:

LDAP directory initialization
-----------------------------

The base directory structure used by DebOps roles is defined and managed by the
:ref:`debops.slapd` Ansible role. The :envvar:`slapd__structure_tasks` variable
contains a list of LDAP objects which will be created during the server
installation, which conform to the :ref:`slapd__ref_acl` configuration.

The :file:`ansible/playbooks/ldap/init-directory.yml` Ansible playbook can be
used to create an admin account in the LDAP directory and to assign it to the
"LDAP Administrator" and "UNIX Administrator" roles. To use it with a newly
configured OpenLDAP server, run the command:

.. code-block:: console

   debops run ldap/init-directory -l <slapd-server>

The playbook will use the current UNIX account information on the Ansible
Controller (username, etc, from the ``passwd`` database and SSH public keys
from :command:`ssh-agent`) to create a new user account with administrative
privileges in the LDAP directory.

The user will first be asked for a new password for the admin account which
will be used in the future to bind to the directory. If no password is provided
or Ansible is run in non-interactive mode, a random password will be generated.

Next, the user will be asked whether the password should be stored on the
Ansible Controller using the Password Store utility. If not, and the password
is randomly generated, it will be stored under the :file:`secret/` hierarchy.
If the password was not randomly generated *and* the Password Store is not
being used, the password will not be stored (under the assumption that it is
memorized) and will have to be provided manually, e.g. using the
``DEBOPS_LDAP_ADMIN_BINDPW`` environment variable, in future playbook runs. See
:ref:`ldap__ref_admin` for further details.

The various defaults used in the playbook can also be overridden on the command
line using the ``--extra-vars`` argument:

.. code-block:: console

   debops run ldap/init-directory -l <slapd-server> --extra-vars="admin_user=ansible admin_use_password_store=False"

The playbook will not make any changes to any existing LDAP entries other than
the administrative user.

.. note:: For the LDAP access to work, the Ansible Controller needs to trust the
   Certificate Authority which is used by the OpenLDAP service. If you rely on
   the :ref:`debops.pki` internal CA, you will have to add the Root CA
   certificate managed by the role to the operating system certificate store.


Example inventory
-----------------

The :ref:`debops.ldap` role is included in the DebOps common playbook,
therefore you don't need to do anything special to enable it on a host. However
it is deactivated by default.

To enable the role, define in the Ansible inventory, for example in the
:file:`ansible/inventory/group_vars/debops_all_hosts/ldap.yml` file:

.. code-block:: yaml

   ldap__enabled: True

The :ref:`debops.ldap` role is used by many other DebOps roles, and enabling it
will affect the environment and configuration of multiple services, including
basic things like UNIX system groups used to manage the host. It's best to
either not enable LDAP support in a given environment, or enable it at the
beginning of a new deployment (but after administrative access has been
configured, as described above).

The POSIX integration with the LDAP directory can be controlled using the
:envvar:`ldap__posix_enabled` variable. If it's set to ``False``, services that
are specific to a POSIX environment (:command:`nslcd`, :command:`sshd`,
:command:`sudo` and others) will not be configured with LDAP support. In such
case only higher-level applications like :command:`nullmailer`, Postfix,
GitLab, etc. will be configured for use with LDAP.

You can of course enable LDAP support in an existing environment, but you
should first learn about changes required by other Ansible roles for successful
migration. Check the documentation of other DebOps roles for more details.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.ldap`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/ldap.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::ldap``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::ldap:tasks``
  Run the LDAP tasks generated by the role in the LDAP directory.


Other resources
---------------

List of other useful resources related to the ``debops.ldap`` Ansible role:

- Manual pages: :man:`ldap.conf(5)`, :man:`ldif(5)`

- `LDAP for Rocket Scientists`__, an excellent book about LDAP and OpenLDAP

  .. __: http://www.zytrax.com/books/ldap/

- `Debian LDAP Portal`__ page in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP

- `Ansible community.general.ldap_entry module`_, used to manage LDAP entries.

- The role does not rely on the Ansible ``ldap_attr`` module, instead it uses
  the ``ldap_attrs`` module included in the ``debops.ansible_plugins`` role to
  manage LDAP attributes of an entry.
