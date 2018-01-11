Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:

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

.. literalinclude:: ../../../../ansible/playbooks/service/dnsmasq-plain.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.dnsmasq`` together with the :ref:`debops.persistent_paths`:

.. literalinclude:: ../../../../ansible/playbooks/service/dnsmasq-persistent_paths.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.dnsmasq`` together with the ``debops-contrib.apparmor`` role:

.. literalinclude:: examples/dnsmasq-apparmor.yml
   :language: yaml

:ref:`debops.persistent_paths` support
--------------------------------------

In case the host in question happens to be a TemplateBasedVM on `Qubes OS`_ or
another system where persistence is not the default, it should be absent in
``debops_service_dnsmasq`` and instead be added to the
``debops_service_dnsmasq_persistent_paths`` Ansible inventory group
so that the changes can be made persistent:

.. code:: ini

   [debops_service_dnsmasq_persistent_paths]
   hostname

The :envvar:`dnsmasq__base_packages` are expected to be present (typically
installed in the TemplateVM).

Note that you will need to set ``core__unsafe_writes`` to ``True`` when you
attempt to update the configuration on a system that uses bind mounts for
persistence. You can set ``core__unsafe_writes`` directly in your inventory
without the need to run the ``debops.core`` role for this special case.
Refer to `Templating or updating persistent files`_ for details.

.. _Templating or updating persistent files: https://docs.debops.org/en/latest/ansible/roles/ansible-persistent_paths/docs/guides.html#templating-or-updating-persistent-files
