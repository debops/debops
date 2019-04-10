Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

By default, the role does not configure any access rules in the
:file:`/etc/security/access.conf` file. Control over this file is initialized
using a configuration entry named ``global``. See the examples in the
:ref:`pam_access__ref_rules` for an explanation how to use it in the Ansible
inventory to set the access rules.

Role is designed to be used by other Ansible roles to manage their own access
lists, with a custom file per service. However, the rules defined via dependent
variables are not tracked outside of the context of a given role (ie. in
different playbooks), and roles cannot affect each other's access rules using
this method. Similarly, in Ansible inventory users should set the state of the
defined rules as ``append``, so that they don't clobber the existing rule files
when the :ref:`debops.pam_access` role is executed on its own, or via
a different playbook.

The activation of the ``pam_access.so`` PAM module for each service is not
managed by the :ref:`debops.pam_access` role itself, and should be managed by
the Ansible roles designed to configure the services.


Example inventory
-----------------

The :ref:`debops.pam_access` role is included in the DebOps common playbook,
therefore you don't need to do anything special to enable it on a host.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.pam_access`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/pam_access.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::pam_access``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.pam_access`` Ansible
role:

- Manual pages: :man:`pam_access(8)`, :man:`access.conf(5)`
