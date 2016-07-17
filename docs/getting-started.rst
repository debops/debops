Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst


Example inventory
-----------------

To `changeme/FIXME**, add the hosts to the
``debops_service_debops_api`` Ansible inventory host group:

.. code:: ini

   [debops_service_debops_api]
   hostname

Example playbook
----------------

Here's an example playbook that can be used to `changeme/FIXME** on a set of hosts:

.. literalinclude:: playbooks/debops_api.yml
   :language: yaml

This playbooks is shipped with this role under
:file:`docs/playbooks/debops_api.yml` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider
using the `DebOps Contrib playbooks`_.
`changeme/FIXME**
In case you use multiple roles maintained by ypid_, consider
using the `ypid-ansible-common`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::debops_api``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::debops_api:pkg``
  Tasks related to system package management like installing, upgrading or
  removing packages.
