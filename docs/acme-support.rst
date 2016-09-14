Automated Certificate Management Environment (ACME)
===================================================

ACME is an initiative designed by Internet Security Research Group for the
`Let's Encrypt <https://letsencrypt.org/>`_ service. It can be used to
provision trusted X.509 certificates in a fully automated way.

One of the challenges to prove control over a domain to an ACME CA server is
called ``http-01`` , which uses a well-known path on the client web server to
serve files which can then be validated by the CA server. This should be
sufficient to prove that a given domain is controlled by the entity that
requests the certificate.

The ``debops.nginx`` Ansible role includes support for the ``http-01`` challenge.
They are enabled by default for all server configurations and can be used to
prove control over specified domains using a ACME client.

Ansible local facts
-------------------

The following ACME related Ansible local facts are exposed by the role:

.. code-block:: none

   ansible_local.nginx.acme
   ansible_local.nginx.acme_root
   ansible_local.nginx.acme_server
   ansible_local.nginx.acme_domain

How ACME support works
----------------------

By default, all servers that have enabled ACME support, will answer queries
on URL:

.. code-block:: none

   http://<domain>/.well-known/acme-challenge/xxxxxxxxxxxxxxxx

These queries will be answered over HTTP. Files will be served from the
particular server ``root`` directory, for example:

.. code-block:: none

   /srv/www/sites/<domain>/public/.well-known/acme-challenge/

If the challenge file is not found at the server location, :program:`nginx` will
switch the request to the "global" server ``root`` directory, by default:

.. code-block:: none

   /srv/www/sites/acme/public/.well-known/acme-challenge/

This directory can be configured in the ``debops.nginx`` default variables, and
is not managed by the role itself. Other Ansible roles are expected to create
it and secure it using UNIX permissions as necessary.

If the requested file is not found on the "global" server ``root`` directory,
the ACME challenge will be redirected over the same protocol (HTTP or HTTPS) to
a different host on configured domain, by default:

.. code-block:: none

   $scheme://acme.{{ nginx_acme_domain }}$request_uri?redirect=yes

The redirected host should provide a configured webserver to respond to the
ACME challenges. A default server is provided in the ``debops.nginx``
configuration and can be enabled on a given host (see below). The additional
parameter ``redirect=yes`` is used by the :program:`nginx` server to detect and
terminate redirect loops.

Manual nginx configuration
--------------------------

The above steps are configured in a separate file on the webserver host:

.. code-block:: none

   /etc/nginx/snippets/acme-challenge.conf

To enable a given :program:`nginx` server to respond to ACME challenges, all you
need to do is to include that file in the ``server {}`` section, for example:

.. code-block:: nginx

   server {
           listen [::]:80

           server_name example.org;

           root /srv/www/sites/example.org/public;

           include snippets/acme-challenge.conf;

           location / {
                   try_files $uri $uri/ /index.html =404;
           }
   }

Above configuration should be sufficient to satisfy local or remote ACME
challenges. Similar configuration can be done on HTTPS server to achieve the
same results.
