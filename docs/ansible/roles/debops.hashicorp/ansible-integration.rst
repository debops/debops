.. _hashicorp__ref_ansible_integration:

Ansible integration
===================

.. include:: ../../../includes/global.rst

.. contents::
   :local:


Support for other Ansible roles
-------------------------------

The ``debops.hashicorp`` Ansible role is designed to be used by other Ansible
roles as role dependency. By design, the application binaries are installed in
the specified path and the rest of the service configuration, including service
process manager configuration, firewall, TCP/UDP port registration in
:file:`/etc/services`, etc. is left to the user or other Ansible roles.

To facilitate seamless role integration, ``debops.hashicorp`` role provides
a set of default variables and Ansible local facts that can be used by other
Ansible roles idempotently. Thus, the modification of the role itself shouldn't
be needed, and it can should be easily integrated in the different playbooks
and environments.


Default variables available to other roles
------------------------------------------

You can use these variables in the playbook to influence the operation of the
``debops.hashicorp`` role from another role:

:envvar:`hashicorp__dependent_packages`
  List of APT packages which should be installed when the ``debops.hashicorp``
  role is executed.

:envvar:`hashicorp__dependent_applications`
  List of HashiCorp_ applications which should be installed by the
  ``debops.hashicorp`` role. For the list of available applications, refer to
  the :envvar:`hashicorp__default_version_map` variable.

:envvar:`hashicorp__consul_webui`
  Boolean variable which enables installation of additional files needed to
  serve the Consul Web UI page. The role will remember the Web UI installation
  state to ensure idempotence.

Examples
~~~~~~~~

In a hypothetical ``consul`` Ansible role create a default variable:

.. code-block:: yaml

   consul__hashicorp_application: 'consul'

Next, in the playbook that executes your role, include the ``debops.hashicorp``
role with your custom variable:

.. code-block:: yaml

   - name: Deploy Consul
     hosts: all
     become: True

     roles:

       - role: debops.hashicorp
         hashicorp__dependent_applications:
           - '{{ consul__hashicorp_application }}'

       - role: consul

This playbook will then install the Consul_ application after verification,
and configure it using your own Ansible role. Make sure that you use YAML list
syntax correctly, otherwise the ``debops.hashicorp`` role will fail due to
wrong variable type mismatch. To install multiple applications at once, you can
use a different variant of the variables and playbook.

The variables, with addition of the Consul Web UI:

.. code-block:: yaml

   consul__hashicorp__dependent_applications: [ 'consul', 'consul-template' ]
   consul__hashicorp__consul_webui: True

The playbook:

.. code-block:: yaml

   - name: Deploy Consul and Consul Template
     hosts: all
     become: True

     roles:

       - role: debops.hashicorp
         hashicorp__dependent_applications: '{{ consul__hashicorp__dependent_applications }}'
         hashicorp__consul_webui: '{{ consul__hashicorp__consul_webui | bool }}'

       - role: consul


Ansible local facts
-------------------

The ``debops.hashicorp`` role maintains a set of Ansible local facts with
information about the installed applications. Other roles can use these facts
in an idempotent way to prepare their own configuration. These facts are:

``ansible_local.hashicorp.installed``
  Boolean. If ``True``, the role has been correctly configured.

``ansible_local.hashicorp.applications``
  YAML dictionary which specifies all currently installed HashiCorp_
  applications as keys and their versions as values.

``ansible_local.hashicorp.bin``
  Path to the directory where binaries are installed, by default
  :file:`/usr/local/bin`.

``ansible_local.hashicorp.consul_webui``
  Boolean. If ``True``, the Consul Web UI files have been downloaded and
  installed.

``ansible_local.hashicorp.consul_webui_path``
  Path to the Consul Web UI files, by default :file:`/srv/www/consul/sites/public`.

Examples
~~~~~~~~

Check if specific HashiCorp_ application is installed on a host:

.. code-block:: yaml

   consul_is_installed: '{{ True
                            if (ansible_local|d() and ansible_local.hashicorp|d() and
                                ansible_local.hashicorp.applications|d() and
                                'consul' in ansible_local.hashicorp.applications.keys())
                            else False }}'

Register the installed application version to conditionally check when the
version changed and restart the daemon:

.. code-block:: yaml

   consul_version: '{{ (ansible_local.hashicorp.applications["consul"]|d())
                        if (ansible_local|d() and ansible_local.hashicorp|d() and
                            ansible_local.hashicorp.applications|d())
                        else "") }}'
