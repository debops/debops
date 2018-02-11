Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

The configuration is split into 3 basic parameters,
this is because of limitation of YAML and easier representation.

- prosody__*_config_global
- prosody__*_config_components
- prosody__*_config_virtual_hosts

By default there are two components active :envvar:`prosody__http_upload` :envvar:`prosody__muc`
Set this varables to false to disable the specific component.

Domains
~~~~~~~

The default virtual host uses :envvar:`prosody__domain` as domain.

The components uses two subdomains: conference.`prosody__domain and upload.`prosody__domain`

Ports
~~~~~

By default the ports are:
- `5222` (c2s)
- `5269` (s2s)
- `5280` http
- `5281` https



Example inventory
-----------------

To enable Prosody server support on a host, it needs to be included in the Ansible inventory in a specific group:

.. code-block:: none

   [debops_service_prosody]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.prosody`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/prosody.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prosody``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
``role::ferm``
  Role tag for configure the firewall ferm.
