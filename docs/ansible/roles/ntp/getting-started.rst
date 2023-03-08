.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

OpenNTPD, ifupdown and systemd integration
------------------------------------------

The ``openntpd`` Debian package provides an :command:`ifupdown` hook,
:file:`/etc/network/if-up.d/openntpd`. It's used to restart the NTP daemon on
any network interface changes so that it can re-bind itself properly.

Unfortunately, the hook is not :command:`systemd`-aware and this causes several
problems:

- During boot, when :command:`ifupdown` configures each interface,
  :command:`systemd` is forced to restart the ``openntpd`` service early each
  time. This might cause dependency problems and leave the NTP daemon service
  in a failed state.

- During :command:`ifupdown` interface reconfiguration, especially when
  multiple interfaces are created or destroyed, the ``openntpd`` service is
  restarted multiple times in rapid succession. This might result in the
  :command:`systemd` not starting the service when it hits the rate limits and
  leaving it in a failed state.

To fix these issues, ``debops.ntp`` role will divert the original ``openntpd``
hook and create its own, which is :command:`systemd`-aware. The hook will only
restart the ``openntpd`` service if it's already running, and will queue the
restart command in the background which should ensure that during interface
configuration NTP daemon is restarted only once, or just a few times and won't
hit rate limits. On boot, the NTP daemon will be started after network
configuration has been completed.

Example inventory
-----------------

To configure the NTP service using the :ref:`debops.ntp` role, a host needs to
be included in the ``[debops_service_ntp]`` Ansible inventory group. An example
inventory can look like this:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_ntp]
   hostname


Example playbook
----------------

Here's an example playbook for using the role without the DebOps playbook:

.. literalinclude:: ../../../../ansible/playbooks/service/ntp.yml
   :language: yaml
   :lines: 1,6-
