Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To install and manage FreeRADIUS on a host, it needs to be included in the
``[debops_service_freeradius]`` Ansible inventory group:

.. code-block:: none

   [debops_service_freeradius]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.freeradius`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/freeradius.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::freeradius``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.freeradius`` Ansible
role:

- Manual pages: :man:`radiusd.conf(5)`, :man:`unlang(5)`
- `FreeRADIUS Getting Started Guide <https://wiki.freeradius.org/guide/Getting-Started>`_
- `FreeRADIUS Technical Guide (PDF) <http://networkradius.com/doc/FreeRADIUS%20Technical%20Guide.pdf>`_
