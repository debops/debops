Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst

Example inventory
-----------------

Hosts added to the ``debops_service_dnsmasq`` inventory group will have the
``dnsmasq`` installed and configured.

.. code:: ini

   [debops_service_dnsmasq]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dnsmasq`` role:

.. literalinclude:: playbooks/dnsmasq-plain.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.dnsmasq`` together with the debops.persistent_paths_ role:

.. literalinclude:: playbooks/dnsmasq-persistent_paths.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.dnsmasq`` together with the debops-contrib.apparmor_ role:

.. literalinclude:: playbooks/dnsmasq-apparmor.yml
   :language: yaml

debops.persistent_paths_ support
--------------------------------

In case the host in question happens to be a TemplateBasedVM on `Qubes OS`_ or
another system where persistence is not the default, it should be absent in
``debops_service_dnsmasq`` and instead be added to the
``debops_service_dnsmasq_persistent_paths`` Ansible inventory group
so that the changes can be made persistent:

.. code:: ini

   [debops_service_dnsmasq_persistent_paths]
   hostname

The :envvar:`dnsmasq__base_packages` are expected to be present (typically installed in the TemplateVM).
