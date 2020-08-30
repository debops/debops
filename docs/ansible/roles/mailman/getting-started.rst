.. Copyright (C) 2014-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Important installation steps
----------------------------

The default installation will configure the Mailman service under
the ``lists.<example.org>`` DNS domain. This can be changed using the
:envvar:`mailman__fqdn` variable.

On installation, if the LDAP support is not enabled, the role will create an
initial superuser account with a random password. The default superuser account
will use the login name specified in the :envvar:`mailman__superuser_name`
variable and e-mail address specified in the :envvar:`mailman__superuser_email`
variable. They are based on the facts defined by the :ref:`debops.core` role,
but you might want to redefine them beforehand in the inventory to be sure that
the validation e-mail is sent to the correct e-mail account.

After the role configures Mailman, you should go to the
https://lists.example.org/ website (make sure that the DNS record is
configured). The default superuser account has a random password assigned to
it, so the first step is to request a password change by specifying your admin
e-mail address. When you get the e-mail, you will be able to specify your own
password. After logging in again, you will receive another e-mail request to
confirm the authenticity of the account - when you confirm that you are who you
say you are in the web interface, you will be able to login as the site
administrator.

The Postorius/HyperKitty web interface uses ``example.com`` as the default
"website" defined in the Django framework. You will have to change that to your
preferred domain using the https://lists.example.org/admin/ interface. In the
Django admin page, in the "Pages" section, click "Modify", "example.com" and
change the default site domain to your preferred one. After this you can create
a new domain for the mailing lists, and a new mailing list in the Postorius web
interface.


LDAP integration
----------------

If the :ref:`LDAP environment <debops.ldap>` is configured on the host, the
role will configure the LDAP support in the Django framework to allow the users
in the :ref:`slapd__ref_acl_group_unix_admins` group to login as superuser
accounts. You should be able to login with your username and password defined
in LDAP directory, and the confirmation e-mail should be sent to your e-mail
account.


.. _mailman__ref_postfix_integration:

SMTP service integration
------------------------

The :ref:`debops.mailman` role provides the configuration for
:ref:`debops.postfix` Ansible role which are used in the example playbook. The
configuration is defined in the :envvar:`mailman__postfix__dependent_maincf`
variable and is passed to the role via role dependent variables.


HTTP service integration
------------------------

The role provides configuration for :ref:`debops.nginx` role which will configure
the Mailman web interface using :program:`nginx` service.

Example inventory
-----------------

To configure Mailman on a host, you need to add it to
``[debops_service_mailman]`` Ansible inventory group. Some other services will
also need to be configured as well. The role integrates with the Postfix service using
the :ref:`debops.postfix` role. A database is needed; role can use either
PostgreSQL or MariaDB service, depending on which one is available. If none of
them are installed, a fallback to SQLite3 database will happen automatically.

An example inventory configuration:

.. code-block:: none

   [debops_all_hosts]
   hostname    ansible_host=hostname.example.org

   [debops_service_postgresql_server]
   hostname

   [debops_service_postfix]
   hostname

   [debops_service_mailman]
   hostname

Example playbook
----------------

The :ref:`debops.mailman` uses a set of other roles to configure additional
services like HTTP and SMTP server. Here's an example playbook with all of the
required DebOps services:

.. literalinclude:: ../../../../ansible/playbooks/service/mailman.yml
   :language: yaml
   :lines: 1,6-
