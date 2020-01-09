Getting started
===============

.. contents::
   :local:

APT preferences configuration
-----------------------------

You can use this role to select a different version of APT packages available
without specifying the version directly in the playbooks or roles. This helps
to ensure that the APT dependency tree is stable and there are no conflicts between
different versions.

Example inventory
-----------------

The ``debops.apt_preferences`` role is included in the :file:`common.yml` playbook, you
can add your own entries to Ansible’s inventory and they should be picked up
automatically on the next playbook run.

Example playbook
----------------

Here's an example playbook that can be used to manage APT preferences:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_preferences.yml
   :language: yaml

