.. _swapfile__ref_getting_started:

Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To enable swap files on a host, it needs to be added to the
``[debops_service_swapfile]`` group in Ansible’s inventory::

    [debops_service_swapfile]
    hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.swapfile`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/swapfile.yml
   :language: yaml
