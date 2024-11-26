.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _ldap__ref_admin:

LDAP tasks and administrative operations
========================================

In addition to maintaining the system-wide LDAP client configuration on a host,
the :ref:`debops.ldap` role can be used to perform tasks in the LDAP directory
itself, using ``ldap_entry`` or ``ldap_attrs`` [#f1]_ Ansible modules. The LDAP
tasks are performed via Ansible task delegation functionality, on the Ansible
Controller. This behaviour can be controlled using the ``ldap__admin_*``
default variables. Check the :ref:`ldap__ref_tasks` documentation for syntax
and examples of usage.


Authentication to the LDAP directory
------------------------------------

The role will use the username of the current Ansible user (from the Ansible
Controller host) as the value of the ``uid=`` attribute to bind to the LDAP
directory. This is done to avoid sharing passwords between users of a single
administrator account in the LDAP directory.

By default LDAP connection will be bound as a Distinguished Name:

.. code-block:: none

   uid=<user>,ou=People,dc=example,dc=org

The DN can be overridden in the :envvar:`ldap__admin_binddn` variable, either
via the Ansible inventory (this should be avoided if the inventory is shared
between multiple administrators), on the command line (using the
``--extra-vars`` argument), or using an environment variable on the Ansible
Controller:

.. code-block:: console

   export DEBOPS_LDAP_ADMIN_BINDDN="cn=ansible,ou=Services,dc=example,dc=org"

How the bind password is obtained is described in the next section. If the bind
password is not provided (the :envvar:`ldap__admin_bindpw` variable is empty),
the LDAP tasks will be skipped. This allows the :ref:`debops.ldap` role to be
used in a playbook with other roles without the fear that lack of LDAP
credentials will break execution of said playbook.


.. _ldap__ref_admin_pass:

Secure handling of LDAP admin credentials
-----------------------------------------

The LDAP password of the current Ansible user is defined in the
:envvar:`ldap__admin_bindpw` inventory variable.

Environment variable
~~~~~~~~~~~~~~~~~~~~
By default, the role first checks if the ``DEBOPS_LDAP_ADMIN_BINDPW``
environment variable is defined on the Ansible Controller and uses its value as
the password during connections to the LDAP directory.

Plaintext file
~~~~~~~~~~~~~~
Next, the role will look for credentials in the :file:`secret/ldap/credentials/`
directory. The files in this directory are named based on the UUID of the
current user's Distinguished Name (see the previous section).

The UUID conversion is done because LDAP Distinguished Names can contain
spaces, and the Ansible lookups don't work too well with filenames that contain
spaces.  You can use the :file:`ldap/get-uuid.yml` playbook to convert user
account DNs or arbitrary LDAP Distinguished Names to an UUID value you can use
to look up the passwords manually, if needed.

In addition, the file :file:`secret/ldap/credentials/debops_ldap_uuid.log` will
contain a list of known UUID-DN mappings (this file is automatically maintained
by the `ldap_password` lookup plugin from :ref:`debops.ansible_plugins`, which
should be used in any role which wishes to create/fetch LDAP credentials).

Password Store
~~~~~~~~~~~~~~
Finally, the role will try and lookup the password using the `passwordstore`__
Ansible lookup plugin. The plugin uses the :command:`pass` `password manager`__
as a backend to store credentials encrypted using the GPG key of the user.

.. __: https://docs.ansible.com/ansible/latest/collections/community/general/passwordstore_lookup.html
.. __: https://www.passwordstore.org/

The path in the :command:`pass` storage directory where the :ref:`debops.ldap`
will look for credentials is defined by the
:envvar:`ldap__admin_passwordstore_path`, by default it's
:file:`debops/ldap/credentials/`. The actual encrypted files with the password
are named based on the UUID, like for the plaintext password.

You can store new credentials in the :command:`pass` password manager using the
:file:`ansible/playbooks/ldap/save-credential.yml` Ansible playbook included
in the DebOps monorepo. All you need to do is run this playbook against one of
the LDAP servers by following this steps:

1. Make sure you have `GPGv2` and `pass` installed, ie. ``apt-get install gpgv2 pass``
2. Make sure you have a `GPG key pair <https://alexcabal.com/creating-the-perfect-gpg-key pair/>`_
3. Initialize the password store: ``pass init <your-gpg-id>``. Example: ``pass init admin@example.com``
4. Run the playbook ``debops run ldap/save-credential -l <host>``
5. Re-run the playbook for each user you want to store a password for

The playbook will ask interactively for the ``uid=`` username, and if not
provided, for the full LDAP Distinguished Name, and after that, for a password
to store encrypted using your GPG key. If you don't specify one, a random
password will be automatically generated, saved in the password store, and
displayed for you to use in the LDAP directory. The encrypted passwords will be stored
by default under ``~/.password-store``.


Different modes of operation
----------------------------

The role acts differently depending on the current configuration of the remote
host and its own environment:

- If the :ref:`debops.ldap` role configuration was not applied on the host, the
  role will set up system-wide LDAP configuration file, and perform the default
  LDAP tasks, tasks defined in the Ansible inventory, and any tasks provided
  via role dependent variables which are usually defined by other roles (see
  :ref:`ldap__ref_dependency` for more details).

- If the :ref:`debops.ldap` role configuration was already applied on the host,
  and there are no LDAP tasks defined by other Ansible roles, the
  :ref:`debops.ldap` role will apply the default LDAP tasks and the tasks from
  Ansible inventory (standalone mode).

- If the :ref:`debops.ldap` role configuration was already applied on the host,
  and the role is used as a dependency for another role, the default LDAP tasks
  and the tasks from Ansible inventory will be ignored, and only those provided
  via the :envvar:`ldap__dependent_tasks` variable by other Ansible roles will
  be executed in the LDAP directory (dependent mode).

This ensures that the list of LDAP tasks is short, and tasks defined by default
in the role, and those defined in the Ansible inventory, which are presumed to
be done previously, are not unnecessarily repeated when dependent role LDAP
tasks are performed.

Because the :ref:`debops.ldap` role relies on the LDAP credentials of the
current Ansible user, the person that executes Ansible does not require full
access to the entire LDAP directory. The role can perform tasks only on
specific parts of the directory depending on the Access Control List of the
LDAP directory server and permissions of the current user.


.. rubric:: Footnotes

.. [#f1] Currently a custom ``ldap_attrs`` module, included in the
         :ref:`debops.ansible_plugins` role is used instead of the
         ``ldap_attr`` plugin included in Ansible.
