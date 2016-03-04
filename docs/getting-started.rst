Getting started
===============

.. contents::
   :local:

SMTP service integration
------------------------

The ``debops.mailman`` role provides configuration variable for
``debops.postfix`` Ansible role (see below). The integration should work with
or without local mail enabled (virtual mail is used if local mail is disabled).
Refer to ``debops.postfix`` documentation for more details.

HTTP service integration
------------------------

The role provides configuration for ``debops.nginx`` role which will configure
the Mailman web interface using ``nginx`` and ``fcgiwrap`` instance (using
``debops.fcgiwrap`` Ansible role). The webserver will be configured with
a restricted list of allowed referers, to prevent hijacking of the web
interface forms by other sites.

Backscatter prevention
----------------------

The default Mailman installation is very prone to `backscatter <https://en.wikipedia.org/wiki/Backscatter_(email)>`_
attacks. Therefore, ``debops.mailman`` will try to reduce this possibility by
taking a few measures:

- some of the mailing list aliases will be disabled by a patch, only
  ``-bounces``, ``-confirm``, ``-owner`` and ``-request`` aliases will be
  present.

- commands from somebody not on the list sent by e-mail will be silently
  discarded using a patch. Unfortunately, this prevents registration via e-mail
  subscribe message, but it was determined that the benefits outweigh the lost
  functionality. Please, use the webinterface for subscription.

- monthly reminders about the mailing list membership are disabled.

Mailman source code modifications
---------------------------------

This role will configure GNU Mailman on the host using the APT ``mailman``
package. The version provided in Debian Wheezy and Debian Jessie packages
requires some additional modifications that are provided as source code
patches. They will be applied automatically in the source code located in
``/usr/lib/mailman/`` directory (this can be disabled by setting the
``mailman__patch`` variable to ``False``).

Modification of the package source code might cause issues during updates,
therefore automatic upgrades of the ``mailman`` package will be disabled in the
``unattended-upgrades`` package using ``debops.unattended_upgrades`` Ansible
role, if patching is enabled.

To apply the patches manually after an upgrade, you can use the provided
Ansible tags, for example:

.. code-block:: console

   user@controller:~$ debops service/mailman --tags role::mailman:patch

The above command will check the status of the patches in Mailman source code
and apply them if necessary.

Language pack support
---------------------

The role contains a Bash language pack conversion script which will be executed
on changes in language pack configuration. Some of the language packs provided
by Debian are stored in wrong encoding (on Debian Wheezy) or contain incorrect
encoding information. The script will try to fix that in the enabled languages
after language packs are generated; however subsequent ``mailman`` package
updates will most likely override these changes. To apply them again you can
use the provided Ansible tags:

.. code-block:: console

   user@controller:~$ debops service/mailman --tags role::mailman:lang

This will re-configure the language pack support in ``mailman`` package and
apply the conversion script changes if necessary.

Example inventory
-----------------

To configure Mailman on a host, you need to add it to
``[debops_service_mailman]`` Ansible inventory group. Example inventory::

    # inventory/hosts
    [debops_service_mailman]
    hostname

Example playbook
----------------

The ``debops.mailman`` uses a set of other roles to configure additional
services like HTTP and SMTP server. Here's an example playbook with all of the
required DebOps services:

.. code-block:: yaml

   ---

   - name: Manage Mailman service
     hosts: [ 'debops_service_mailman' ]
     become: True

     roles:

       - role: debops.fcgiwrap
         tags: [ 'role::fcgiwrap' ]
         fcgiwrap__instances:
           - '{{ mailman__fcgiwrap__instance }}'

       - role: debops.unattended_upgrades
         tags: [ 'role::unattended_upgrades' ]
         unattended_upgrades__dependent_blacklist: '{{ mailman__unattended_upgrades__dependent_blacklist }}'

       - role: debops.apt_preferences
         tags: [ 'role::apt_preferences' ]
         apt_preferences__dependent_list:
           - '{{ mailman__apt_preferences__dependent_list }}'
           - '{{ nginx__apt_preferences__dependent_list }}'

       - role: debops.ferm
         tags: [ 'role::ferm' ]
         ferm__dependent_rules:
           - '{{ postfix__ferm__dependent_rules }}'
           - '{{ nginx__ferm__dependent_rules }}'

       - role: debops.postfix
         tags: [ 'role::postfix' ]
         postfix__dependent_lists:    '{{ mailman__postfix__dependent_lists }}'
         postfix__dependent_maincf:   '{{ mailman__postfix__dependent_maincf }}'
         postfix__dependent_mastercf: '{{ mailman__postfix__dependent_mastercf }}'

       - role: debops.nginx
         tags: [ 'role::nginx' ]
         nginx__servers: '{{ mailman__nginx__servers }}'

       - role: debops.mailman
         tags: [ 'role::mailman' ]

