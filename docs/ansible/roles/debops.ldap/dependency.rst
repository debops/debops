.. _ldap__ref_dependency:

Use as a dependent role
=======================

The :ref:`debops.ldap` role is designed to be used as an API between Ansible
roles and the LDAP directory. Roles can define a list of :ref:`LDAP tasks <ldap__ref_tasks>`
which are passed to the :ref:`debops.ldap` role using role dependent variables
on the playbook level. These LDAP tasks will be executed using the
:ref:`ldap__ref_admin` interface in the LDAP directory.

This API allows the LDAP integration to be focused in a single, specific role
(:ref:`debops.ldap`), so that other Ansible roles don't have to implement
different ways of accessing and manipulating the LDAP directory by themselves.
The LDAP data like passwords, names of objects and attribute values can be
defined by the "parent" role in its own variables, and passed to the
:ref:`debops.ldap` role to create or change LDAP objects as needed.

.. note::
   Examples of usage and integration between roles will be provided in the
   future using existing DebOps roles.


.. _ldap__ref_dit:

LDAP directory structure organized by DebOps
--------------------------------------------

LDAP directory has a hierarchical structure defined by objects and their
attributes. Various Ansible roles included in DebOps can interface with the
LDAP directory to create or maintain their own set of objects and attributes.
The hierarchy of these objects is called the `Directory Information Tree`__.

.. __: https://en.wikipedia.org/wiki/Directory_information_tree

Each DebOps role that is integrated with the :ref:`debops.ldap` role defines
a special page in its documentation section, :file:`ldap-dit.rst`. In this
file, users can find a human-readable description of the LDAP objects and their
attributes, which are linked to their corresponding role default variables and
Ansible local facts. This can be used to quickly locate the relevant source of
a particular LDAP object or attribute.

The objects and attributes have example values and Distinguished Names, real
objects in the LDAP directory will be named differently depending on the
configuration, but the general structure of the LDAP directory should be
accurately reflected in the documentation.

The DIT documentation of different roles is cross-referenced between the roles
that interact with each other at the LDAP directory level. This allows
travelsal between the documentation pages of different roles to quickly find
parent and child nodes, and see the relation between them.

The :ref:`root of the DebOps DIT <ldap__ref_ldap_dit>` is defined by the
:ref:`debops.ldap` Ansible role. Other roles will rely on it as a dependency,
and will use the Ansible local facts defined by this role to create their own
LDAP objects. Some of these roles will have their own "child" roles that depend
on them, and so on.
