.. Copyright (C) 2015      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To enable the :command:`dovecot` service on a host, you need to add it to the
``[debops_service_dovecot]`` Ansible inventory group:

.. code-block:: none

    [debops_service_dovecot]
    hostname


Default setup
-------------

If you don't specify any configuration values, the role will setup
:command:`dovecot` with `IMAP`, `IMAPS`, `LMTP`__, `Sieve`__ and `Quota`__
support.

In addition, `LDAP` will automatically be enabled if the host is already
configured to use :ref:`debops.ldap`, otherwise :command:`dovecot` will be
configured to allow every user which is able to login via PAM to also login
via IMAP and access their emails.

.. __: https://doc.dovecot.org/configuration_manual/protocols/lmtp_server/
.. __: https://doc.dovecot.org/configuration_manual/sieve/pigeonhole_sieve_interpreter/
.. __: https://doc.dovecot.org/configuration_manual/quota/


Other resources
---------------

List of other useful resources related to the ``debops.dovecot`` Ansible role:

- Manual pages: for example, :man:`dovecot(1)`, :man:`doveconf(1)` and
  :man:`doveadm(1)`

- The website of the `Dovecot Project`__, in particular the `configuration
  documentation`__

.. __: https://www.dovecot.org/
.. __: https://doc.dovecot.org/


Example playbook
----------------

If you are using the role without DebOps, here's an example Ansible playbook
that uses the ``debops.dovecot`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dovecot.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible runs. This can be used after a host is first
configured to speed up playbook execution when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::dovecot``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
``role::dovecot:conf``
  Main configuration tag, should be used in the playbook to execute all of
  the role tasks relates to configuration creation.
``role::dovecot:conf:sql``
  `SQL` specific configuration subtag.
``role::dovecot:conf:ldap``
  `LDAP` specific configuration subtag.
``role::dovecot:user``
  Limited to :command:`dovecot` user configuration tasks.
``role::dovecot:group``
  Limited to :command:`dovecot` group configuration tasks.
