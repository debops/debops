Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To enable the :command:`nslcd` service on a host, you need to add it to the
``[debops_service_nslcd]`` Ansible inventory group. The host should also be
configured with base LDAP support via the :ref:`debops.ldap` role (see its
documentation for more details):

.. code-block:: none

   [debops_service_ldap]
   hostname

   [debops_service_nslcd]
   hostname

A common case is configuration of LDAP authentication in the entire cluster of
hosts. You can enable :command:`debops.nslcd` role on all DebOps hosts in the
Ansible inventory at once:

.. code-block:: none

   [debops_all_hosts]
   hostname1
   hostname2

   [debops_service_nslcd:children]
   debops_all_hosts

The :command:`nslcd` service can also be installed and configured by other
playbooks, for example ``bootstrap-ldap.yml``. In such cases the custom
playbook will configure the :command:`nslcd` service on a host, but the role
playbook will not work on a host automatically; you will have to include that
host in the ``[debops_service_nslcd]`` Ansible inventory group via one of the
methods above to be able to change the service configuration.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nslcd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nslcd.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::nslcd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.nslcd`` Ansible role:

- Manual pages: :man:`nslcd.conf(5)`

- LDAP support in DebOps: :ref:`client-side <debops.ldap>`, :ref:`server-side <debops.slapd>`

- `LDAP/NSS setup instructions`__ in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP/NSS#NSS_Setup_with_libnss-ldapd

- `LDAP/PAM setup instructions`__ in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP/PAM

- `LDAP authentication`__ documentation in the Arch Wiki

  .. __: https://wiki.archlinux.org/index.php/LDAP_authentication

- `Debian LDAP Portal`__ page in the Debian Wiki

  .. __: https://wiki.debian.org/LDAP
