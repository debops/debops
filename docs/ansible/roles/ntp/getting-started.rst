Getting started
===============

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

``debops.ntp`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

Example playbook
----------------

Here's an example playbook for using the role without the DebOps playbook:

.. literalinclude:: ../../../../ansible/playbooks/service/ntp.yml
   :language: yaml
