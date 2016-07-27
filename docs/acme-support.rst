Automated Certificate Management Environment (ACME)
===================================================

ACME is an initiative designed by Internet Security Research Group for the
`Let's Encrypt <https://letsencrypt.org/>`_ service. It can be used to
provision trusted X.509 certificates in a fully automated way.

One of the methods to authenticate to an ACME CA server is so called "webroot"
method, which uses a well-known path on the client web server to serve ACME
challenges which can then be validated by the CA server. This should be
sufficient to prove that a given subdomain is owned by the entity that requests
the certificate.

The ``debops.nginx`` Ansible role includes support for ACME challenge queries.
They are enabled by default for all server configurations and can be used to
automatically sign specified domains using the "webroot" method of official
``letsencrypt`` client or other ACME clients.

Role default variables
----------------------

This is a list of ``debops.nginx`` default variables that are used to control
ACME support:

``nginx_acme``
  Bool. Enable or disable support for ACME on all ``nginx`` servers. This can
  be overriden using ``item.acme`` variable in the server configuration
  dictionary. ``nginx_acme`` variable is enabled by default.

``nginx_acme_root``
  Path to global ``root`` directory on the host which will be used to serve
  ACME challenges. By default, ``/srv/www/sites/acme/public``.

``nginx_acme_server``
  Bool. Enable or disable configuration of ACME ``nginx`` server that will
  respond to the challenges on the configured DNS domain.

``nginx_acme_domain``
  DNS domain which will be used to redirect ACME challenges from hosts to
  a specific URL, by default ``acme.{{ ansible_domain }}``.

The values of above variables are also stored in Ansible local ``nginx`` facts
on the remote host and can be accessed by Ansible variables::

    ansible_local.nginx.acme
    ansible_local.nginx.acme_root
    ansible_local.nginx.acme_server
    ansible_local.nginx.acme_domain

How ACME support works
----------------------

By default, all servers that have enabled ACME support, will answer queries
on URL::

    http://<domain>/.well-known/acme-challenge/xxxxxxxxxxxxxxxx

These queries will be answered over HTTP. Files will be served from the
particular server ``root`` directory, for example::

    /srv/www/sites/<domain>/public/.well-known/acme-challenge/

If the challenge file is not found at the server location, ``nginx`` will
switch the request to the "global" server ``root`` directory, by default::

    /srv/www/sites/acme/public/.well-known/acme-challenge/

This directory can be configured in the ``debops.nginx`` default variables, and
is not managed by the role itself. Other Ansible roles are expected to create
it and secure it using UNIX permissions as necessary.

If the requested file is not found on the "global" server ``root`` directory,
the ACME challenge will be redirected over the same protocol (HTTP or HTTPS) to
a different host on configured domain, by default::

    $scheme://acme.{{ nginx_acme_domain }}$request_uri?redirect=yes

The redirected host should provide a configured webserver to respond to the
ACME challenges. A default server is provided in the ``debops.nginx``
configuration and can be enabled on a given host (see below). The additional
parameter ``redirect=yes`` is used by the ``nginx`` server to detect and
terminate redirect loops.

Manual nginx configuration
--------------------------

The above steps are configured in a separate file on the webserver host::

    /etc/nginx/snippets/acme-challenge.conf

To enable a given ``nginx`` server to respond to the ACME challenges, all you
need to do is to include that file in the ``server {}`` section, for example::

    server {
            listen [::]:80

            server_name example.org;

            root /srv/www/sites/example.org/public;

            include snippets/acme-challenge.conf;

            location / {
                    try_files $uri $uri/ /index.html =404;
            }
    }

Above configuration should be sufficient to perform local or remote ACME
challenges. Similar configuration can be done on HTTPS server to achieve the
same results.

