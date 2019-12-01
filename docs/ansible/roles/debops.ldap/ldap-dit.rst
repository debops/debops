.. _ldap__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.ldap` Ansible role fits in the
:ref:`ldap__ref_dit`.


Directory structure
-------------------

- :envvar:`DNS (example.org) <ldap__domain>`

  - :ref:`rootDSE <slapd__ref_ldap_dit>` -> :ref:`debops.slapd`

    - :envvar:`dc=example,dc=org <ldap__base_dn>` (:envvar:`LDAP tasks <ldap__default_tasks>`)

      - :envvar:`ou=Hosts <ldap__hosts_rdn>`

        - :envvar:`dNSDomain=example.org <ldap__device_domain_rdn>` (:envvar:`conditional <ldap__device_separate_domains>`)

          - :envvar:`cn=host.example.org <ldap__device_self_rdn>` (:envvar:`conditional <ldap__device_enabled>`)

            - :ref:`uid=dokuwiki <dokuwiki__ref_ldap_dit>` -> :ref:`debops.dokuwiki`
            - :ref:`uid=gitlab <gitlab__ref_ldap_dit>` -> :ref:`debops.gitlab`
            - :ref:`uid=nslcd <nslcd__ref_ldap_dit>` -> :ref:`debops.nslcd`
            - :ref:`uid=nextcloud <owncloud__ref_ldap_dit>` -> :ref:`debops.owncloud`
            - :ref:`uid=nullmailer <nullmailer__ref_ldap_dit>` -> :ref:`debops.nullmailer`
            - :ref:`uid=postfix <postldap__ref_ldap_dit>` -> :ref:`debops.postldap`
            - :ref:`uid=saslauthd <saslauthd__ref_ldap_dit>` -> :ref:`debops.saslauthd`
            - :ref:`uid=sshd <sshd__ref_ldap_dit>` -> :ref:`debops.sshd`
            - :ref:`uid=sudo <sudo__ref_ldap_dit>` -> :ref:`debops.sudo`

      - :envvar:`ou=People <ldap__people_rdn>`
      - :envvar:`ou=Groups <ldap__groups_rdn>`

        - :ref:`cn=DokuWiki Administrators <dokuwiki__ref_ldap_dit>` -> :ref:`debops.dokuwiki`

      - :envvar:`ou=Machines <ldap__machines_rdn>`
      - :envvar:`ou=Services <ldap__services_rdn>`

      - :envvar:`ou=Roles <ldap__roles_rdn>`

        - ``cn=Password Reset Agent`` (via the :file:`ldap/init-directory.yml` playbook)

          - ``roleOccupant``: :ref:`uid=nextcloud,cn=host.example.org,... <owncloud__ref_ldap_dit>` -> :ref:`debops.owncloud`


Object Classes and Attributes
-----------------------------

- :envvar:`dNSDomain=example.org <ldap__device_domain_rdn>`

  - :ref:`debops.ldap`: :envvar:`Object Classes <ldap__device_domain_object_classes>`, :envvar:`Attributes <ldap__device_domain_attributes>`

- :envvar:`cn=host.example.org <ldap__device_self_rdn>`

  - :ref:`debops.ldap`: :envvar:`Object Classes <ldap__device_object_classes>`, :envvar:`Attributes <ldap__device_attributes>`
  - :ref:`debops.sshd`: :envvar:`Object Classes <sshd__ldap_device_object_classes>`, :envvar:`Attributes <sshd__ldap_device_attributes>` (SSH host public keys)


Parent nodes
------------

There are no parent nodes defined for the :ref:`debops.ldap` Ansible role.


Child nodes
-----------

- :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>`

- :envvar:`ansible_local.ldap.basedn <ldap__basedn>`

- :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>`

- :envvar:`ansible_local.ldap.hosts_rdn <ldap__hosts_rdn>`

- :envvar:`ansible_local.ldap.people_rdn <ldap__people_rdn>`

- :envvar:`ansible_local.ldap.system_groups_rdn <ldap__system_groups_rdn>`

- :envvar:`ansible_local.ldap.groups_rdn <ldap__groups_rdn>`

- :envvar:`ansible_local.ldap.machines_rdn <ldap__machines_rdn>`

- :envvar:`ansible_local.ldap.roles_rdn <ldap__roles_rdn>`

- :envvar:`ansible_local.ldap.services_rdn <ldap__services_rdn>`
