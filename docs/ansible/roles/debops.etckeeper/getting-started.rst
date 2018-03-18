Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

By default :command:`git` is used as VCS. This can be changed by the inventory
variables :envvar:`etckeeper__vcs`.

The role is designed with :command:`etckeeper` being already installed on
a host in mind. This can be done for example via Debian Preseeding or LXC
template installing and pre-configuring :command:`etckeeper`; the role will
keep the already existing configuration without any changes if the variables
are not overwritten through the Ansible inventory. Any changes in the
:file:`/etc/`` directory will be automatically committed by Ansible local facts
before Ansible role execution.

Example inventory
-----------------

.. code-block:: YAML

   ## If you don’t want to track hashed passwords.
   etckeeper__ignore_host_group_list:
     - 'shadow'
     - 'shadow-'

In Ansible's inventory.

Example playbook
----------------

Here's an example playbook that uses the ``debops.etckeeper`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/etckeeper.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::etckeeper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::etckeeper:vcs_config``
  Run tasks related to configuring VCS options.
