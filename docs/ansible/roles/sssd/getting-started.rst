.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To enable the :command:`sssd` service on a host, you need to add it to the
``[debops_service_sssd]`` Ansible inventory group. The host should also be
configured with base LDAP support via the :ref:`debops.ldap` role (see its
documentation for more details):

.. code-block:: none

   [debops_service_ldap]
   hostname

   [debops_service_sssd]
   hostname

A common case is configuration of LDAP authentication in the entire cluster of
hosts. You can enable :command:`debops.sssd` role on all DebOps hosts in the
Ansible inventory at once:

.. code-block:: none

   [debops_all_hosts]
   hostname1
   hostname2

   [debops_service_sssd:children]
   debops_all_hosts

The :command:`sssd` service can also be installed and configured by other
playbooks, for example ``bootstrap-sss.yml``. In such cases the custom
playbook will configure the :command:`sssd` service on a host, but the role
playbook will not work on a host automatically; you will have to include that
host in the ``[debops_service_sssd]`` Ansible inventory group via one of the
methods above to be able to change the service configuration.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.sssd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/sssd.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::sssd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.sssd`` Ansible role:

- Manual pages: :man:`sssd.conf(5)` (and subsystem man pages such as
  :man:`sssd-ldap(5)` and :man:`sssd-krb5(5)`)

- The website of the `SSSD Project`__

  .. __: https://sssd.io/

- LDAP support in DebOps: :ref:`client-side <debops.ldap>`, :ref:`server-side <debops.slapd>`

- `Configuring SSSD`__ in the Red Hat Enterprise Linux 7 Guide

  .. __: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system-level_authentication_guide/sssd

- `Understanding SSSD`__ in the Red Hat Enterprise Linux 8 Guide

  .. __: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/configuring_authentication_and_authorization_in_rhel/understanding-sssd-and-its-benefits_configuring-authentication-and-authorization-in-rhel

- `LDAP authentication`__ documentation in the Arch Wiki

  .. __: https://wiki.archlinux.org/index.php/LDAP_authentication

- `Debian LDAP Portal`__ page in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP
