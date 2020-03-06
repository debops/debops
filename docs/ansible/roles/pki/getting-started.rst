.. Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Ansible Controller requirements
-------------------------------

Some operations performed by the ``debops.pki`` role are done on the Ansible
Controller. However, DebOps roles are not designed to manage the Ansible Controller
host directly, so they cannot automatically install the required software.

Software packages required by the role on the Ansible Controller::

    bash >= 4.3.0
    openssl >= 1.0.1

.. Note that the role asserts that required dependencies are met. In case you
   change the required versions here, remember to update them in
   `../tasks/main.yml` as well.

Initial configuration
---------------------

The default configuration of the ``debops.pki`` role and the environment it creates
is designed to automatically provide valid X.509 certificates within the DebOps
cluster – a central Certificate Authority located on the Ansible Controller
automatically signs certificate requests from remote hosts, which are uploaded
by Ansible to the :file:`secret/` directory. Signed certificates are downloaded to
the remote hosts and automatically enabled, when necessary.

All of the remote hosts managed by DebOps will have the internal Root
Certificate Authority certificate installed in the system CA store. This will
ensure that the hosts within the cluster will automatically trust each other
and encrypted communication within the cluster should be possible without
further intervention.

Because of the nature of how X.509 certificates are created and maintained
(they cannot be "updated", per se, only new ones can be issued by the CA), it's
a good practice to create a test deployment of the PKI, and check if the
generated certificates are acceptable (correct Distinguished Name, certificate
validity times, etc.). There are some important role variables which might need
to be set in the inventory for best results.

Maintaining a secure Certificate Authority is a complicated process and to
ensure secure operation additional steps might be needed. You should read the
rest of the ``debops.pki`` documentation to find out which parts of the created
environment are sensitive and require additional steps to ensure secure
operation.

Useful global parameters
------------------------

The environment managed by the ``debops.pki`` role is distributed between the
Ansible Controller and remote hosts. Due to how task delegation in Ansible is
designed, some of the variables that are important for the operation of the
Ansible Controller are "sourced" on remote hosts. Therefore it's a good
practice to define them in the Ansible inventory ``all`` group (usually
:file:`ansible/inventory/group_vars/all/pki.yml`) for consistency between different
remote hosts.

Most of these variables are related to Certificate Authority operation, the
ones you will likely want to change are:

:envvar:`pki_ca_domain`
  This is the DNS domain used as a base for the internal Certificate Authority
  Distinguished Names. If you use more than one domain in your environment, you
  should set this variable to your preferred domain on all hosts, through
  Ansible's inventory.

  If you use VPS hosts provided by an external organization, they might be
  configured with no default domain, or the provider domain might be set up by
  default. Make sure that you check what domain is used by your remote hosts.

:envvar:`pki_ca_organization`
  This is the organizations name used as a base for the internal
  Certificate Authority Distinguished Names.

:envvar:`pki_ca_root_dn`, :envvar:`pki_ca_domain_dn`, :envvar:`pki_ca_service_dn`
  These variables define the Distinguished Name or Subject of the Root
  Certificate Authority and Domain Certificate Authority. The value is a list
  of DN entries which define the subject.

:envvar:`pki_authorities`
  This is the list of internal Certificate Authorities managed on an Ansible
  Controller.

  ``debops.pki`` now supports the X.509 Name Constraints certificate extension by
  default. This may break software using old version of OpenSSL and multi-domain
  environments. Please see ``name_constraints`` and ``name_constraints_critical``
  under :ref:`pki__ref_authorities` for more information.

Example inventory
-----------------

In DebOps, the ``debops.pki`` role is included in the :file:`common.yml` playbook
and is run automatically on all of the managed hosts. You don't need to
specifically enable it in Ansible's inventory.

Example playbook
----------------

The ``debops.pki`` role requires a specialized Ansible playbook for correct
operation. Additional directories required by the role are created in the
:file:`secret/` directory on Ansible Controller, and this requires use of the
special ``debops.pki/env`` role provided within the main role.

.. literalinclude:: ../../../../ansible/playbooks/service/pki.yml
   :language: yaml
   :lines: 1,6-


.. _pki__ref_realm_renewal:

Renewing Certificates
---------------------

For renewing certificates, just

1. remove file:`/etc/pki/realms/<realm>/` from the remote host and
2. re-run debops.pki against it, e.g. this::

     debops service/pki  --limit=$REMOTE_HOST

This will create a new key for the remote host.
If you use external keys, they will be preserved
