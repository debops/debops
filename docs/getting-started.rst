Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

A host needs to be added to Ansible inventory to allow it to be bootstrapped,
but you don't need to specify a group for it:

.. code-block:: none

    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops.bootstrap`` role::

    ---
    - name: Bootstrap hosts for Ansible management
      hosts: [ 'all:!localhost' ]

      roles:

        - role: debops.bootstrap

How to bootstrap a host with DebOps
-----------------------------------

Within main DebOps playbooks, ``bootstrap`` is a separate playbook which is not
run by default by main playbook. To use it with a new host which has only
a ``root`` account and requires a password, you can run the playbook like this::

.. code-block:: shell

    debops bootstrap --limit host --user root --ask-pass

Bootstrap playbook does not have specific host restrictions, so it will be
executed on all hosts (apart from ``localhost``) if not limited, which you
should avoid as done in the example using ``--limit host``.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::bootstrap:packages``
  Execute tasks related to package installation.

``role::bootstrap:admin``
  Execute tasks related to setting up the admin user.

``role::bootstrap:hostname``
  Execute tasks related to configuring the hostname.
