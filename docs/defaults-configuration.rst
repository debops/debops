Default variables: configuration
================================

Some of ``debops.pki`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _pki_private_groups_present:

pki_private_groups_present
--------------------------

This list can be used to create system groups that otherwise could be not
present when the PKI realm is managed. For example another role creates custom
user/group that maintains its own service certificates, but in order to do
that, ``debops.pki`` is used to manage the PKI realm. but at the moment that
the ``debops.pki`` role is run by Ansible, custom group does not exist, so the
Ansible run stops. Therefore, you can create system groups beforehand using
this list.

You can define the system groups as simple items, or dictionary values with
parameters:

``name``
  The name of the group to create.

``system``
  Bool, by default ``True``. Specify if a given group is a system group.

``when``
  The value of this variable is checked as a bool (``True``/``False``) to
  determine if a given system group should be created or not. You can use this
  as a condition to, for example, create groups only on specific hosts.

Examples
~~~~~~~~

Ensure two system groups exist, one with a condition:

.. code-block:: yaml

   pki_private_groups_present:

     - 'group1'

     - name: 'group2'
       when: '{{ inventory_hostname in specific_inventory_group }}'

