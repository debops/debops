.. _rabbitmq_server__ref_dependency:

Usage as a role dependency
==========================

The ``debops.rabbitmq_server`` role can be used as a dependency by other
Ansible roles to manage RabbitMQ main configuration file idempotently.
Configuration options from multiple roles can be merged together and included
in the configuration file, or removed conditionally.

.. contents::
   :local:


Dependent role variables
------------------------

The role exposes three default variables that can be used by other Ansible
roles as dependent variables:

:envvar:`rabbitmq_server__dependent_role`
  Required. Name of the role that uses the ``debops.rabbitmq_server`` as
  a dependency. This will be used to store the configuration in its own YAML
  dictionary. The selected name shouldn't be changed, otherwise configuration
  will be desynchronized.

:envvar:`rabbitmq_server__dependent_config`
  Required. List of the RabbitMQ configuration options defined in the same
  format as the main configuration. See :ref:`rabbitmq_server__ref_config` for
  more details.

:envvar:`rabbitmq_server__dependent_state`
  Optional. If not specified or ``present``, the configuration will be included
  in the :file:`/etc/rabbitmq/rabbitmq.config` configuration file and
  stored as Ansible local fact. if ``absent``, the configuration will be
  removed from the generated configuration file.


Dependent configuration storage and retrieval
---------------------------------------------

The dependent configuration from other roles is stored in the :file:`secret/`
directory on the Ansible Controller (see :ref:`debops.secret` for more details) in
a JSON file, with each role configuration in a separate dictionary. The
``debops.rabbitmq_server`` role reads this file when Ansible local facts
indicate that the RabbitMQ service is installed, otherwise a new empty file is
created.  This ensures that the stale configuration is not present on a new or
re-installed host.

The YAML dictionaries from different roles are be merged with the main
configuration in the :envvar:`rabbitmq_server__combined_config` variable that
is used to generate the final configuration. The merge order of the different
``rabbitmq_server__*_config`` variables allows to further affect the dependent
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
