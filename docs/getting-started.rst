Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

Host needs to be added to Ansible inventory to be able to be bootstrapped, but
you don't need to specify a group for it::

    hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.bootstrap`` role::

    ---
    - name: Bootstrap hosts for Ansible management
      hosts: all:!localhost

      roles:

        - role: debops.bootstrap

How to bootstrap a host with DebOps
-----------------------------------

Within main DebOps playbooks, ``bootstrap`` is a separate playbook which is not
run by default by main playbook. To use it with a new host which has only
a ``root`` account and requires password, you can run the playbook like this::

    debops bootstrap -l host -u root -k

Bootstrap playbook does not have specific host restrictions, so it will be
executed on all hosts (apart from ``localhost``) if not limited, which you
should avoid.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::bootstrap:hostname``
  Execute tasks related to configuring the hostname.
