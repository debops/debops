.. Copyright (C) 2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Default configuration
---------------------

The service will be configured to serve media files from the
:file:`/var/lib/minidlna` directory. You might want to include additional media
directories in the configuration, see :ref:`minidlna__ref_configuration`
variable documentation for details and examples.

MiniDLNA uses `Simple Service Discovery Protocol`__ to advertise its presence
on the network. The service is advertised via the 239.255.255.250 multicast
address over 1900/udp port and clients that want to use the DLNA service need
to have this port opened in their firewalls to receive the advertisements.

Keep in mind that SSDP protocol might be used for DDoS reflection attacks if
not properly secured; you should grant access to this port only from trusted
networks.

.. __: https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol

Example inventory
-----------------

To enable MiniDLNA service on a host it needs to be included in the specific Ansible
inventory group:

.. code-block:: none

   [debops_service_minidlna]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.minidlna`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/minidlna.yml
   :language: yaml
   :lines: 1,5-
