.. Copyright (C) 2015-2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents:: Sections
      :local:

Default configuration
---------------------

The ``debops.gitlab`` role supports installation of GitLab Omnibus Community
Edition as well as the Enterprise Edition, which can be selected using the
:envvar:`gitlab__edition` variable. Manual installation of the GitLab Omnibus
package is also supported, in which case the role can be used to configure such
installation and provide integration with the rest of the environment.

The initial ``root`` password is randomly generated and stored in the
:file:`ansible/secret/gitlab/credentials/` directory on the Ansible Controller,
managed by the :ref:`debops.secret` Ansible role.

GitLab Omnibus deployed by DebOps will be configured with GitLab Container
Registry available by default on a separate TCP port. This ensures that only
one DNS domain and X.509 certificate is needed by default. Container Registry
can be deployed on a separate DNS domain if needed.

The role integrates GitLab Omnibus with the :command:`ferm` service through the
:ref:`debops.ferm` Ansible role. By default, the main GitLab service and
Container Registry are accessible to any hosts and networks once deployed, this
can be configured using role variables.

PKI environment managed by the :ref:`debops.pki` role is also integrated with
GitLab Omnibus, via the use of symlinks in :file:`/etc/gitlab/ssl/` directory
that provide access to private keys and X.509 certificates in the
:file:`/etc/pki/realms/` directories.

If the LDAP environment managed by the :ref:`debops.ldap` Ansible role is
detected, a suitable user account for GitLab instance will be created by
default. GitLab will be configured with a single LDAP server in that case.

Daily backups of GitLab Omnibus environment will be enabled by default using
the :command:`cron` service.


Example inventory
-----------------

To install GitLab Omnibus service on a host, it needs to be included in the
``[debops_service_gitlab]`` Ansible inventory group.

Example Ansible inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_gitlab]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.gitlab`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/gitlab.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::gitlab``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.gitlab`` Ansible role:

- Official documentation of `GitLab Omnibus`__

  .. __: https://docs.gitlab.com/omnibus/

- GitLab `package repository`__ which contains APT packages for older releases,
  not accessible through the official APT configuration

  .. __: https://packages.gitlab.com/gitlab/gitlab-ce/
