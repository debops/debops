Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

``debops.atd`` will install the ``at`` Debian package which provides the ``atd``
service as well as commands that allow you to schedule jobs at a specific
time or when the host CPU load average is below a specific threshold.

By default the interval of the ``batch`` command checking if jobs can be run, as
well as the level of CPU utilization which halts job scheduling are somewhat
randomized to "smooth out" CPU utilization on hosts with multiple virtual
machines and/or containers. See the default variables for the minimum and
maximum values for each.

After installation, the role creates a ``/etc/at.allow`` file which only enables the use
of the ``at`` and ``batch`` commands by the Ansible admin account (superuser
has implicit access). You can either add specific users to this list by using
``atd_*_allow`` list variables, or enable access by all users not listed in
``/etc/at.deny`` by defining ``atd_default_allow`` as empty list (``[]``).

Example inventory
-----------------

``debops.atd`` is included by default in the ``common.yml`` DebOps playbook;
you don't need to do anything to have it installed.

If you want to disable the ``atd`` service on a host or set of hosts, you can do
this by the setting variable::

    atd_enabled: False

in Ansible's inventory.

Example playbook
----------------

Here's an example playbook that can be used to enable and manage the ``atd``
service on a set of hosts::

    ---
    - name: Configure atd service
      hosts: debops_atd
      become: True

      roles:

        - role: debops.atd
          tags: [ 'role::atd' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after the host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::atd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks.

``role::atd:users``
  Configure contents of ``/etc/at.allow`` and ``/etc/at.deny`` configuration
  files.

