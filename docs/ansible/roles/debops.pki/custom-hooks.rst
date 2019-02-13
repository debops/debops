.. _custom_hooks:

Custom hook scripts
===================

The :program:`pki-realm` script supports usage of a custom hook scripts located in
the :file:`/etc/pki/hooks/` directory. These scripts will be executed in alphabetical
order (see :man:`run-parts(8)` for more details) within a special environment. You
can use that to perform operations after certain actions like creation of a new
PKI realm, or activation of a new certificate.

Execution environment
---------------------

The hook scripts will be executed by the ``root`` account inside the PKI hook
directory (:file:`/etc/pki/hooks/`), with a set of ``$PKI_SCRIPT_*`` environment
variables:

``$PKI_SCRIPT_REALM``
  Contains the name of the current PKI realm.

``$PKI_SCRIPT_FQDN``
  Contains Fully Qualified Domain Name used as the default domain if the realm
  does not specify one in it's name.

``$PKI_SCRIPT_SUBJECT``
  Contains the Distinguished Name, or subject of the certificate, each element
  separated by the ``/`` character, similar to the format of the ``openssl req
  -subj`` option.

``$PKI_SCRIPT_DOMAINS``
  List of apex (root) domains configured for the realm, separated by the ``/``
  character.

``$PKI_SCRIPT_SUBDOMAINS``
  List of subdomains which should be added to each apex domain, each one
  separated by the ``/`` character. The special ``_wildcard_`` name means
  a wildcard subdomain (``*.example.com``).

``$PKI_SCRIPT_PRIVATE_KEY``
  Absolute path to the private key of the current PKI realm.

``$PKI_SCRIPT_DEFAULT_CRT``
  Absolute path to the current PKI realm certificate chain, expected to be used
  in the application configuration files.

``$PKI_SCRIPT_DEFAULT_KEY``
  Absolute path to the current PKI realm private key, expected to be used in
  the application configuration files.

``$PKI_SCRIPT_DEFAULT_PEM``
  Absolute path to the current PKI realm combined private key and certificate
  chain, expected to be used in the application configuration files.

``$PKI_SCRIPT_STATE``
  A list of PKI realm states separated by the ``,`` character. You can inspect
  this variable to determine the current state of the realm (initialization,
  activation of new certificates, changed files) and react to it in the script.

Known script states
-------------------

You can use the ``$PKI_SCRIPT_STATE`` variable to check current state of the
PKI realm. This variable should always be non-empty, otherwise hook scripts are
not executed. Each state can repeat multiple times on the list, but you should
avoid multiple execution due to a particular state.

List of known states:

``new-realm``
  A new PKI realm has been initialized, there are no private keys or
  certificates present.

``new-private-key``
  A private key has been generated.

``new-internal-request``
  A new internal CA certificate signing request has been generated.

``new-acme-request``
  A new ACME certificate signing request has been generated.

``changed-certificate``
  A new certificate has been activated, or there has been change of the active
  Certificate Authority (internal, external, acme).

``changed-dhparam``
  Diffie-Hellman parameters in the certificate chain have been added/updated.

``file-change``
  A generic file change notification.

``file-deletion``
  A file has been deleted.

``changed-public-file``
  Some of the files in :file:`public/` directory have been changed/replaced.

``changed-private-file``
  Some of the files in :file:`private/` directory have been changed/replaced.

Example nginx hook
------------------

This is an example hook script which detects if a given PKI realm is currently
used by the :program:`nginx` server and if so, when a certificate change is detected
it reloads the :program:`nginx` daemon so that new certificate can be activated.

.. code-block:: bash

   #!/bin/bash

   # Reload or restart nginx on a certificate state change

   set -o nounset -o pipefail -o errexit

   nginx_config="/etc/nginx/nginx.conf"
   nginx_sites="/etc/nginx/sites-enabled"
   nginx_action="reload"

   # Check if current PKI realm is used by the 'nginx' webserver
   certificate=$(grep -r "${PKI_SCRIPT_DEFAULT_CRT:-}" ${nginx_sites}/* || true)

   # Get list of current realm states
   states=( $(echo "${PKI_SCRIPT_STATE:-}" | tr "," " ") )

   if [ -n "${certificate}" -a "${#states[@]}" -gt 0 ] ; then

       for state in "${states[@]}" ; do

           if [ "${state}" = "changed-certificate" -o "${state}" = "changed-dhparam" ] ; then

               # Check if current init is systemd
               if $(pidof systemd > /dev/null 2>&1) ; then

                   nginx_state="$(systemctl is-active nginx.service)"
                   if [ ${nginx_state} = "active" ] ; then
                       if $(/usr/sbin/nginx -c ${nginx_config} -t > /dev/null 2>&1) ; then
                           systemctl ${nginx_action} nginx.service
                       fi
                   fi

               else

                   nginx_pidfile="$(grep -E '^pid\s+' ${nginx_config} | awk '{print $2}' | cut -d\; -f1)"
                   if $(kill -0 $(<${nginx_pidfile}) > /dev/null 2>&1) ; then
                       if $(/usr/sbin/nginx -c ${nginx_config} -t > /dev/null 2>&1) ; then
                           service nginx ${nginx_action}
                       fi
                   fi

               fi

               break
           fi

       done

   fi
