.. Copyright (C) 2021 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.ghostunnel`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _ghostunnel__services:

ghostunnel__services
--------------------

List of ``ghostunnel`` services that should be present given host, each one
defined as a YAML dict. Each "service" can define either one end of a connection.
Additional parameters can also be specified for other roles, such as firewall
configuration and registering a service in ``/etc/services`` database.

common parameters
~~~~~~~~~~~~~~~~~

``name``
    String, required. Defines a name of the service, which is used as the name of
    the configuration file and service name in ``/etc/services`` as well as
    systemd service name.

    You should use only letters, numbers and a dash (-) character. You should pick
    an unique name for each service, preferably unique across your entire
    infrastructure. Check getent services database to avoid collisions with
    existing names.

``mode``
    String, required. It accepts ``server`` value or ``client`` value.

    Server mode (TLS listener -> plain TCP/UNIX target).
    Client mode (plain TCP/UNIX listener -> TLS target).

``listen``
    String, required. Address and port to listen on (can be HOST:PORT, unix:PATH, systemd:NAME
    or launchd:NAME).

``target``
    String, required. Address to forward connections to (can be HOST:PORT or unix:PATH).

``shutdown_timeout``
    String, optional. Graceful shutdown timeout. Terminates after timeout even if connections
    still open. ``5m`` by default.

    For services that keep connections open like Elasticseearch, set a shutdown timeout in
    ``1s`` for correct ``Ghostunnel`` service restarts.

``connect_timeout``
    String, optional. Timeout for establishing connections, handshakes. ``10s`` by default.

``quiet``
    List or string, optional. Silence log messages (can be ``all``, ``conns``, ``conn-errs``,
    ``handshake-errs``; or list for more than one). ``conns`` by default.

server mode parameters
~~~~~~~~~~~~~~~~~~~~~~

``allow_all``
    Boolean, optional. Allow all clients, do not check client cert subject.

``allow_cn``
    List or string, optional. Allow clients with given common name.

``allow_ou``
    List or string, optional. Allow clients with given organizational unit name.

``allow_dns``
    List or string, optional. Allow clients with given DNS subject alternative name.

``allow_uri``
    List or string, optional. Allow clients with given URI subject alternative name.

``allow``
    List, optional. List of IP addresses or CIDR subnets which will be allowed to connect to
    the service.

    If it's empty and not ``disable_authentication``, remote connections are
    allowed.

    If it's empty and ``disable_authentication`` is used, remote connections are
    not allowed.

``disable_authentication``
    Boolean, optional. Disable client authentication, no client certificate will be required.
    If ``False``, the default, at least one access control flag (allow-{all, cn, ou, dns, uri})
    is required.

``unsafe_target``
    Boolean, optional. If set, does not limit target to localhost, 127.0.0.1, [::1], or UNIX
    sockets. ``False`` by default.

client mode parameters
~~~~~~~~~~~~~~~~~~~~~~

``verify_cn``
    List or string, optional. Allow servers with given common name.

``verify_ou``
    List or string, optional. Allow servers with given organizational unit name.

``verify_dns``
    List or string, optional. Allow servers with given DNS subject alternative name.

``verify_uri``
    List or string, optional. Allow servers with given URI subject alternative name.

``disable_authentication``
    Boolean, optional. Disable client authentication, no certificate will be provided to the server.
    ``False`` by default.

``unsafe_target``
    Boolean, optional. If set, does not limit listen to localhost, 127.0.0.1, [::1], or UNIX
    sockets. ``False`` by default.

``override_server_name``
    String, optional. If set, overrides the server name used for hostname verification.

``connect-proxy``
    String, optional. If set, connect to target over given HTTP CONNECT proxy. Must be HTTP/HTTPS URL.
