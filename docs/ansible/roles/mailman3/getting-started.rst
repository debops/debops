.. Copyright (C) 2020 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:

Database integration
--------------------

The role currently configures these databases through debconf:

- mariadb
- postgresql
- sqlite3

The role will configure the MariaDB or PostgreSQL database if the
:ref:`debops.mariadb_server` or :ref:`debops.postgresql_server` roles have been
run against the host, falling back to a SQLite 3 database. Note that external
databases are not supported at this time.

LDAP support
------------

If the host has been configured with :ref:`debops.ldap`, this role will set up
LDAP authentication in the Mailman 3 web frontend. The backend for this
functionality is provided by `django-auth-ldap`__. The default configuration
will allow full administrative access to the members of the 'UNIX
Administrators' group.

.. __: https://django-auth-ldap.readthedocs.io/en/latest/

A local administrator with (by default) username 'admin' and a random password
is created to allow list administration when the LDAP server cannot be used.

SMTP service integration
------------------------

The role provides configuration for the :ref:`debops.postfix` role. This
dependent configuration sets Postfix up for LMTP delivery to Mailman Core.

HTTP service integration
------------------------

The role provides configuration for the :ref:`debops.nginx` role that will
configure the Postorius web interface using :program:`nginx` and ``uWSGI``.

Example inventory
-----------------

To configure Mailman Suite on a host, you need to add it to the
``[debops_service_mailman3]`` Ansible inventory group. Example inventory::

    # inventory/hosts
    [debops_service_mailman3]
    hostname

Example playbook
----------------

:ref:`debops.mailman3` uses a set of other roles to configure additional
services like the HTTP and SMTP server. Here is an example playbook with all of
the required DebOps services:

.. literalinclude:: ../../../../ansible/playbooks/service/mailman3.yml
   :language: yaml
   :lines: 1,5-
