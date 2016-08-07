Default variable details
========================

Some of ``debops.debops_fact`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _debops_fact__ref_facts:

debops_fact__*_facts
--------------------

The ``debops_fact__*_facts`` lists contain information about Ansible local
facts managed by the role. The facts are stored in two dictionary variables:

``ansible_local.debops_fact.*``
  This dictionary variable contains "public" facts, readable by everyone.

``ansible_local.debops_fact_priv.*``
  This dictionary variable contains "private" facts, readable only by ``root``
  user. You can use ``debops_fact__private_group`` variable to allow access to
  a different UNIX group if desired.

Each entry on the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the fact to configure, should only contain alphanumeric
  characters and underscoe (``_``) character.

``value``
  Required. The value of the fact to configure. Different value types act
  differently in certain combinations. See :ref:`debops_fact__ref_fact_values`
  for more details.

``state``
  Optional. If not specified or ``present``, role will ensure that the
  specified values are present in a given fact, depending on their type.

  If ``absent``, role will remove the specified values from a given fact if
  they are present.

``fact_state``
  Optional. If not specified or ``present``, a given fact will be configured on
  a host. If ``absent``, specified fact will be removed from the Ansible local
  facts.

Examples
~~~~~~~~

Create a public fact with an email address:

.. code-block:: yaml

   debops_fact__public_facts:
     - name: 'email_address'
       value: 'root@{{ ansible_domain }}'


Create a public fact with a list of paths:

.. code-block:: yaml

   debops_fact__public_facts:
     - name: 'custom_paths'
       value: [ '/dir1', '/dir2', '/dir3' ]


Create a private fact with a YAML dictionary of users and passwords:

.. code-block:: yaml

   debops_fact__private_facts:
     - name: 'user_passwords'
       value:
         user1: 'password1'
         user2: 'password2'


Remove an element from a list in a public fact:

.. code-block:: yaml

   debops_fact__public_facts:
     - name: 'custom_paths'
       state: 'absent'
       value: [ '/dir2' ]


Remove a key from a private fact containing a YAML dictionary:

.. code-block:: yaml

   debops_fact__private_facts:
     - name: 'user_passwords'
       state: 'absent'
       value:
         user2: 'password2'


Remove a fact from private facts:

.. code-block:: yaml

   debops_fact__private_facts:
     - name: 'user_passwords'
       fact_state: 'absent'


.. _debops_fact__ref_fact_values:

Ansible local fact values
-------------------------

The role processes public and private fact lists in order, and applies them to
existing Ansible local facts. Different variable and fact values react
differently to each other. This is done to protect existing facts from
mismatched variables.

If there are no specific facts for a given variable, it will be created

If a ``string`` variable is applied to a ``string`` fact, the fact will be
replaced.

If a ``string`` variable is applied to a ``list`` fact, the string will be
appended to the list.

If a ``string`` variable is applied to a ``dictionary`` fact, the string is
discarded.

If a ``list`` variable is applied to a ``string`` fact, the list is discarded.

If a ``list`` variable is applied to a ``list`` fact, both lists are merged
together.

If a ``list`` variable is applied to a ``dictionary`` fact, the list is
discarded.

If a ``dictionary`` variable is applied to a ``string`` fact, the dictionary is
discarded.

If a ``dictionary`` variable is applied to a ``list`` fact, the dictionary is
discarded.

If a ``dictionary`` variable is applied to a ``dictionary`` fact, both
dictionaries are combined. Lists on the first dictionary level are merged
together, strings replace other strings, dictionaries on the first dictionary
level ale combined together.
