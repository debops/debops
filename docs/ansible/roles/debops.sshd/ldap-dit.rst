.. _sshd__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.sshd` Ansible role fits in the
:ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=sshd <sshd__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=sshd <sshd__ldap_self_rdn>`

  - :ref:`debops.sshd`: :envvar:`Object Classes <sshd__ldap_self_object_classes>`, :envvar:`Attributes <sshd__ldap_self_attributes>`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`sshd__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`sshd__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.sshd` Ansible role.
