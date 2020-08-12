.. Copyright (C) 2020 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

The default configuration of this role will install isc-dhcp-relay, configure
it to listen on the internal network interface and forward requests to the
default IPv4 gateway. A DHCP server should be running on the default IPv4
gateway; if not, you should change the :envvar:`dhcrelay__servers` variable.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dhcrelay`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dhcrelay.yml
   :language: yaml
   :lines: 1,6-

Other resources
---------------

It is worth checking out the dhcrelay manpage: :man:`dhcrelay(8)`.
