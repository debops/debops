.. _etc_aliases__ref_dependency:

Usage as a role dependency
==========================

The ``debops.etc_aliases`` role can be used as a dependency by other Ansible
roles to manage contents of the :file:`/etc/aliases` file idempotently.
Configuration options from multiple roles can be merged together and included
in the alias database, or removed conditionally.

.. contents::
   :local:


Dependent role variable
-----------------------

The role exposes the :envvar:`etc_aliases__dependent_recipients` variable which
can be used to define mail aliases and recipients by other Ansible roles
through the role dependent variables.

The variable is a YAML list with YAML dictionaries as entries. A short format
of the configuration uses the dictionary key as a name of the dependent role
and dictionary value as that role's configuration, in the format defined by
:ref:`etc_aliases__ref_recipients` variable (see playbook excerpt below):

.. code-block:: yaml

   roles:

     - role: debops.etc_aliases
       etc_aliases__dependent_recipients:
         - role_name: '{{ role_name__etc_aliases__dependent_recipients }}'

The extended version of the configuration uses a YAML dictionary with specific
parameters:

``role``
  Required. Name of the role, used to save its configuration in a YAML
  dictionary on the Ansible Controller. Shouldn't be changed once selected,
  otherwise the configuration will be desynchronized.

``config``
  Required. YAML list with configuration of the aliases and recipients in the
  same format defined by :ref:`etc_aliases__ref_recipients` variable.

``state``
  Optional. If not specified or ``present``, the configuration will be included
  in the generated alias database. If ``absent``, the configuration will be
  removed from the alias database. If ``ignore``, a given configuration entries
  will be skipped during alias evaluation and won't affect any existing
  entries.

An example extended configuration (playbook excerpt):

.. code-block:: yaml

   roles:

     - role: debops.etc_aliases
       etc_aliases__dependent_recipients:
         - role: 'role_name'
           config: '{{ role_name__etc_aliases__dependent_recipients }}'

The above configuration layout allows for use of the multiple role dependencies
in one playbook by providing configuration of each role in a separate
configuration entry.


Dependent configuration storage and retrieval
---------------------------------------------

The dependent configuration from other roles is stored in the :file:`secret/`
directory on the Ansible Controller (see :ref:`debops.secret` for more details) in
a JSON file, with each role configuration in a separate dictionary. The
``debops.etc_aliases`` role reads this file when Ansible local facts
indicate that the :file:`/etc/aliases` file is configured, otherwise a new
empty file is created. This ensures that the stale configuration is not present
on a new or re-installed host.

The YAML dictionaries from different roles are be merged with the main
configuration in the :envvar:`etc_aliases__combined_recipients` variable that
is used to generate the final configuration. The merge order of the different
``etc_aliases__*_recipients`` variables allows to further affect the dependent
configuration through Ansible inventory if necessary, therefore the Ansible
roles that use this method don't need to provide additional variables for this
purpose themselves.


Example role default variables
------------------------------

.. literalinclude:: examples/application-defaults.yml
   :language: yaml


Example role playbook
---------------------

.. literalinclude:: examples/application-playbook.yml
   :language: yaml
