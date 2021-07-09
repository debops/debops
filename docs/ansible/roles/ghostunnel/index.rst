.. Copyright (C) 2021 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later
.. _debops.ghostunnel:

debops.ghostunnel
=================

Ghostunnel__ is a simple TLS proxy with mutual authentication support for
securing non-TLS backend applications.

Ghostunnel supports two modes, client mode and server mode. Ghostunnel in
server mode runs in front of a backend server and accepts TLS-secured
connections, which are then proxied to the (insecure) backend. A backend
can be a TCP domain/port or a UNIX domain socket. Ghostunnel in client mode
accepts (insecure) connections through a TCP or UNIX domain socket and proxies
them to a TLS-secured service. In other words, ghostunnel is a replacement for
``stunnel``.

``debops.ghostunnel`` installs ``ghostunnel`` binary and configures systemd
services for server mode and client mode.

.. __: https://github.com/ghostunnel/ghostunnel

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/ghostunnel/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
