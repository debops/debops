.. _roundcube__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:

.. _roundcube__ref_default_setup:

Default setup
-------------

If you don't specify any configuration values, the role will setup a Nginx_
HTTP server running a default installation of the latest Roundcube stable
release which is then accessible via ``https://webmail.<your-domain>``.
SQLite is used as database backend for storing the user settings.


.. _roundcube__ref_srv_records:

IMAP and SMTP server detection
------------------------------

The role detects the preferred IMAP and SMTP servers by checking the DNS SRV
resource records (as defined by the :rfc:`6186`), looking for the IMAPS and
SMTPS (submission) service recommended by the :rfc:`8314` using Implicit TLS.
The example DNS resource records checked by the role:

.. code-block:: none

   _imaps._tcp          SRV 0 1 993 imap.example.org.
   _submissions._tcp    SRV 0 1 465 smtp.example.org.

At the moment only a single SRV resource record is supported by the role.

If the above SRV resource records are not available, the
:ref:`debops.roundcube` role will check for the presence of the
:ref:`debops.dovecot` and the :ref:`debops.postfix` role Ansible local facts on
the host. If they are found, the respective service (IMAP and/or SMTP
(submission)) will be configured to be accessed via the host's own FQDN address
to support X.509 certificate verification. In this case the services will also
use Implicit TLS (ports 993 and 465 respectively).

If both SRV resource records and local Ansible facts are not available, the
:ref:`debops.roundcube` role will fall back to using static subdomains for the
respective services, based on the host domain:

.. code-block:: none

   IMAP: imap.example.org
   SMTP: smtp.example.org

This allows for deployment of the RoundCube Webmail independent from the
respective services, for example on a separate host or VM. The communication
with the mail services will be encrypted by default using Implicit TLS.


.. _roundcube__ref_example_inventory:

Example inventory
-----------------

To install and configure Roundcube on a host, it needs to be present in the
``[debops_service_roundcube]`` Ansible inventory group. Additional services
like :ref:`memcached <debops.memcached>`, :ref:`Redis <debops.redis_server>`
and :ref:`MariaDB database <debops.mariadb_server>` can help increase the
website performance.

.. code-block:: none

   [debops_all_hosts]
   webmail

   [debops_service_mariadb_server]
   webmail

   [debops_service_memcached]
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
