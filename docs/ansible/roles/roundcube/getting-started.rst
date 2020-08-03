.. Copyright (C) 2016-2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2016-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _roundcube__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:

.. _roundcube__ref_default_setup:

Default setup
-------------

If you don't specify any configuration values, the role will setup a Nginx_
HTTP server running a default installation of the latest Roundcube stable
release which is then accessible via ``https://webmail.<your-domain>``.
SQLite is used as database backend for storing the user settings.

When the :ref:`LDAP infrastructure <debops.ldap>` is detected on the Roundcube
host, the role will install and configure LDAP support in Roundcube. The
default address book will be configured to allow only searches in the
directory, which is benefical in larger environments. The ``password`` plugin
will be enabled and configured to use the LDAP Password Modify Extended
Operation (:rfc:`3062`) driver to allow users to change their passwords.

Roundcube will use the current user credentials to login to the LDAP directory,
therefore access to the LDAP entries and attributes depends on the LDAP ACL
configuration in the directory itself.

Local spell check support will be configured using the `Enchant`__ library with
``aspell`` spell checker. By default only the English dictionary
(``aspell-en``) is installed, more dictionaries can be added using the
:envvar:`roundcube__packages` variable.

.. __: https://en.wikipedia.org/wiki/Enchant_(software)


.. _roundcube__ref_private_repo:

Deployment from private or internal git repository
--------------------------------------------------

The :ref:`debops.roundcube` role supports deployment of Roundcube from
private/internal :command:`git` repositories over HTTPS. This can be useful
when a Roundcube codebase is forked to include custom themes or other changes
in the application required for a particular installation.

To do this, you can specify the URL to the :command:`git` repository using the
:envvar:`roundcube__git_repo` variable in the form:

.. code-block:: none

   https://<username>:<password>@<git-host>/<organization>/<repository>.git

In GitLab, this functionality is called `Deploy Tokens`__, while on GitHub
users can create `Personal Access Tokens`__. The tokens can be generated
per-project and allow for read-only access to the :command:`git` repository.

.. __: https://docs.gitlab.com/ce/user/project/deploy_tokens/
.. __: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

The access credentials will be stored in the :file:`.git/` directory of the
cloned Roundcube repository. The role by default puts it in the location
specified by the :envvar:`roundcube__git_dir` variable, under the
:file:`/usr/local/src/` subdirectories, with access restricted via UNIX
permissions.

The role expects that the checked out commits or tags are signed by a valid GPG
key. To include the GPG keys for the staff that creates the modifications of
the Roundcube code base, you can include their GPG fingerprints in the
:envvar:`roundcube__git_additional_gpg_keys` list. They will be imported to the
Roundcube UNIX account by the :ref:`debops.keyring` role.

Here are an example Ansible inventory variables that hide the token using the
:ref:`debops.secret` role:

.. code-block:: yaml

   roundcube_access_token: '{{ lookup("file", secret + "/roundcube/access_token") }}'
   roundcube__git_repo: '{{ "https://" + roundcube_access_token
                            + "@code.example.org/mail-infra/roundcubemail.git" }}'
   roundcube__git_additional_gpg_keys: [ 'fingerprint1', 'fingerprint2' ]

Before running the role, make sure to put the credentials in the
:file:`ansible/secret/roundcube/access_token` file inside of the DebOps project
directory. The file should contain the credentials in the form of:

.. code-block:: none

   <username>:<password>

There should be no new line character at the end.


.. _roundcube__ref_srv_records:

IMAP, SMTP and Sieve server detection
-------------------------------------

The role detects the preferred IMAP, SMTP and Sieve servers by checking the DNS
SRV resource records (as defined by the :rfc:`6186` and :rfc:`5804`), looking
for the IMAPS and SMTPS (submission) service recommended by the :rfc:`8314`
using Implicit TLS. The example DNS resource records checked by the role:

.. code-block:: none

   _imaps._tcp          SRV 0 1 993  imap.example.org.
   _submissions._tcp    SRV 0 1 465  smtp.example.org.
   _sieve._tcp          SRV 0 1 4190 sieve.example.org.

At the moment only a single SRV resource record is supported by the role.

If the above SRV resource records are not available, the
:ref:`debops.roundcube` role will check for the presence of the
:ref:`debops.dovecot` and the :ref:`debops.postfix` role Ansible local facts on
the host. If they are found, the respective service (IMAP, SMTP (submission)
and/or Sieve) will be configured to be accessed via the host's own FQDN address
to support X.509 certificate verification. In this case the services will also
use Implicit TLS (ports 993 and 465 respectively).

If both SRV resource records and local Ansible facts are not available, the
:ref:`debops.roundcube` role will fall back to using static subdomains for the
respective services, based on the host domain:

.. code-block:: none

   IMAP:  imap.example.org
   SMTP:  smtp.example.org
   Sieve: sieve.example.org

This allows for deployment of the RoundCube Webmail independent from the
respective services, for example on a separate host or VM. The communication
with the mail services will be encrypted by default using Implicit TLS.


.. _roundcube__ref_example_inventory:

Example inventory
-----------------

To install and configure Roundcube on a host, it needs to be present in the
``[debops_service_roundcube]`` Ansible inventory group. Additional services
like :ref:`memcached <debops.memcached>`, :ref:`Redis <debops.redis_server>`,
:ref:`MariaDB <debops.mariadb_server>` and
:ref:`PostgreSQL <debops.postgresql_server>` can help increase the website
performance.

.. code-block:: none

   [debops_all_hosts]
   webmail

   [debops_service_mariadb_server]
   webmail

   [debops_service_memcached]
   webmail

   [debops_service_postgresql_server]
   webmail

   [debops_service_redis_server]
   webmail

   [debops_service_roundcube]
   webmail


.. _roundcube__ref_example_playbook:

Example playbook
----------------

The following playbook can be used with DebOps. If you are using these role
without DebOps you might need to adapt them to make them work in your setup.

.. literalinclude:: ../../../../ansible/playbooks/service/roundcube.yml
   :language: yaml
   :lines: 1,5-

This playbook is also shipped with DebOps at :file:`ansible/playbooks/service/roundcube.yml`.


.. _roundcube__ref_ansible_tags:

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::roundcube``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::roundcube:pkg``
  Run tasks related to system package installation.

``role::roundcube:deployment``
  Run tasks related to the application deployment and update.

``role::roundcube:config``
  Run tasks related to the Roundcube application configuration.

``role::roundcube:database``
  Run tasks related to setup or update the database user and schema.
