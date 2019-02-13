Default variable details
========================

.. include:: ../../../includes/global.rst
.. include:: includes/role.rst

Some of ``debops.apache`` default variables have more extensive configuration
than simple strings or lists. Here you can find documentation and examples for
them.

.. This section is intended to be similar to the docs in debops.nginx. If you
   modify this section, consider also checking debops.nginx if the same also
   applies there, please.

.. note:: This section of the documentation might not be fully up-to-date. If
   there is something missing you are encouraged to cross-check with
   :ref:`debops.nginx` docs and enhance the documentation.

.. contents::
   :local:
   :depth: 2


.. _apache__ref_modules:

apache__modules
---------------

The Apache modules configuration is represented as YAML dictionaries. Each key of
those dictionaries is a module name.
The module names correspond to the file names under :file:`/etc/apache2/mods-available`
Refer to the `Apache module index`_ for a full list of available modules upstream.

The role provides multiple variables which can be used on different inventory
levels. The :envvar:`apache__combined_modules` variable combines these YAML
dictionaries together and determines the order in which module configuration
"mask" the previous onces.

The dictionary value can be a simple boolean corresponding to the ``enabled``
option (as described below) or a dictionary by itself with the following
supported options:

``enabled``
  Required, boolean. Defaults to ``True``.
  Set to ``{{ omit }}`` not change the state of a module.
  Whether the module should be enabled or disabled in Apache.

``force``
  Optional, boolean. Defaults to ``False``.
  Force disabling of default modules and override Debian warnings when set to ``True``.

``config``
  Optional, string.
  Module configuration directives which will be saved in a role managed
  configuration file under :file:`conf-available` and contained in a
  ``<IfModule>`` section which causes Apache to only enables this module
  configuration when the module is enabled.

``ignore_configcheck``
  Optional, boolean. Defaults to ``False``.
  Ignore configuration checks about inconsistent module configuration.
  Especially for mpm_* modules.

Examples
~~~~~~~~

Ensure the ``ldap`` module is enabled for the given host:

.. code-block:: yaml

   apache__host_modules:
     ldap: True


.. _apache__ref_snippets:

apache__snippets
----------------

Apache configuration snippets are represented as YAML dictionaries. Each key of those
dictionaries corresponds to the filename prefix under :file:`conf-available`.
The :file:`.conf` file extension is added by the role and must be omitted by
the user.
Note that Debian maintainers recommend in :file:`README.Debian` of the
``apache2`` package that filenames should be prefixed with :file:`local-` to
avoid name clashes with files installed by packages. This is not enforced by
the role and should be done by the user of the role.

The role provides multiple variables which can be used on different inventory
levels. The :envvar:`apache__combined_snippets` variable combines these YAML
dictionaries together and determine the order in which configuration
"mask" the previous onces.

The dictionary value can be a simple boolean corresponding to the ``enabled``
option (as described below) or a dictionary by itself with the following
supported options:

``enabled``
  Optional, boolean. Defaults to ``True`` unless ``item.state`` is set to ``absent``.
  Whether the configuration snippet should be enabled or disabled in Apache
  server context.

``state``
  Optional, String. Defaults to ``present``.
  Whether the module should be ``present`` or ``absent`` in the :file:`conf-available` directory.

``type``
  Optional, string.
  Refer to the following subsections for the supported type.


Type: raw
~~~~~~~~~

Available when ``item.type`` is set to ``raw`` or ``divert``.
This can be used to create a snippet based on the ``item.raw`` content.

``raw``
  Optional, string.
  Raw content to write into the snippet file.
  By default, the role will look under
  :file:`templates/etc/apache2/conf-available` for a template matching the item
  key.
  If ``raw`` is specified, a special template will be used which simply
  writes the given content into the snippet.
  Refer to the `Apache configuration sections documentation`_ for details.


Type: divert
~~~~~~~~~~~~

Available when ``item.type`` is set to ``divert``.
This special type does not create a snippet file, instead it uses
:command:`dpkg-divert` to allow you to do a package management aware rename of a snippet.

Note that for this type no changes are done in the :file:`conf-enabled`
directory to avoid idempotency issues with a potential snippet with the
same filename as the snippet which is diverted away.

``divert_suffix``
  Optional, string. Defaults to ``.dpkg-divert``.
  Allows to change the suffix for the diverted file in the
  :file:`sites-available` directory.

``divert_filename``
  Optional, string. The default value is determined based on the values of
  ``item.name`` and ``item.filename``.
  Allows to change the divert filename.

``divert``
  Optional, string. Defaults to the file path determined for snippet in the
  :file:`conf-available` directory.
  Allows to specify a full file path where to divert the file to.
  Note that the ``item.divert_suffix`` is still in affect when using this option.


Type: dont-create
~~~~~~~~~~~~~~~~~

This special type assumes the snippet file is already present and does not try
to create it.
This can be used to enable or disable snippet files managed by system packages
for example.


Examples
~~~~~~~~

Ensure the given Apache directives are configured in
:file:`/etc/apache2/conf-available/example.conf` and enabled in Apache server
context:

.. code-block:: yaml

   apache__host_snippets:
     example:
       type: 'raw'
       raw: |
         # Your raw Apache directives.


Ensure the :file:`/etc/apache2/conf-available/owncloud.conf` snippet shipped by
ownCloud system packages is disabled so that ``debops.owncloud`` has full control
over it and can enable ownCloud in specific vhost contexts.

.. code-block:: yaml

   owncloud__apache__dependent_snippets:
     owncloud:
       enabled: False
       type: 'dont-create'


.. _apache__ref_vhosts:

apache__vhosts
--------------

The Apache virtual hosts can be defined as lists of YAML dictionaries. This
allows the configuration of Apache virtual hosts on different inventory
levels as needed.

Note that one vhost item of this role usually results in two Apache virtual
hosts, one for HTTP and one for HTTPS.

Common role options
~~~~~~~~~~~~~~~~~~~

``name``
  Required, string or list of strings.
  Domain names to for this name-based virtual host.

  The first element is used to create the name of the sites configuration file
  and must be a normal domain name, other elements can include wildcards.

  The list can also be empty (but needs to be defined) in which case the
  configuration it is included in will be named :file:`default`.

``filename``
  Optional, string.
  Alternative name of the sites configuration file under the
  :file:`/etc/apache2/sites-available/` directory. The suffix :file:`.conf` will be
  added automatically. This can be used to distinguish different server
  configurations for the same ``item.name``. For example separate
  configuration for HTTP and HTTPS.

``enabled``
  Optional, boolean. Defaults to ``True``.
  Specifies if the configuration should be enabled by creating a symlink in
  :file:`/etc/apache2/sites-enabled/`.

``state``
  Optional, string. Defaults to ``present``.
  Whether the vhost should be ``present`` or ``absent``.

``by_role``
  Optional, string. Name of a Ansible role in the format ``ROLE_OWNER.ROLE_NAME`` which is
  responsible for the server configuration.

``comment``
  Optional, string. Comment for the intended purpose of the virtual host.

``type``
  Optional, string. Specify name of the template to use to generate the virtual
  host configuration. Templates can extend other templates.


.. _apache__ref_vhost_common_webserver_options:

Common webserver options
~~~~~~~~~~~~~~~~~~~~~~~~

.. _apache__ref_vhost_server_admin:

``server_admin``
  Optional, string.
  Defaults to :envvar:`apache__server_admin`.
  Default server admin contact information. Either a Email address or a URL
  (preferable on another webserver if this one fails).

``index``
  Optional, string or boolean (``False``).
  Space separated list of index filenames.
  The directive will be omitted if set to ``False``.

``root``
  Optional, string.
  Absolute path to server root to use for this server configuration.
  Defaults to :file:`/srv/www/<``name[0]>/public/`.
  See also ````owner`` parameter.
  The directive will be omitted if set to ``False``.

``document_root``
  Optional, string. Alias for ``item.root``.
  ``item.root`` is also used by :ref:`debops.nginx` and might be preferred for that
  reason.

``alias``
  Optional, string.
  Alias to ``item.root`` configured using the `Alias directive`_.

``root_directives``
  Optional, string.
  Additional raw Apache directives to apply to ``item.root``.

``options``
  Optional, string. Defaults to :envvar:`apache__vhost_options`.

``allow_override``
  Optional, string. Defaults to :envvar:`apache__vhost_allow_override`.

``listen_http``
  Optional, list of strings/integers.
  Defaults to a socket based on :envvar:`apache__http_listen` matching all network addresses.
  List of ports, IP addresses or sockets this server configuration should
  listen on for HTTP connections.

``listen_https``
  Optional, list of strings/integers.
  Defaults to a socket based on :envvar:`apache__https_listen` matching all network addresses.
  List of ports, IP addresses or sockets this server configuration should
  listen on for HTTPS connections.

``include``
  Optional, string or list of strings.
  The given files are included the appropriate virtual host context using the
  `Include directive`_.

``include_optional``
  Optional, string or list of strings.
  The given files are included the appropriate virtual host context using the
  `IncludeOptional directive`_.

``raw_content``
  Optional, string.
  Allows to specify raw Apache directives which are inlined in the appropriate
  virtual host context.

Redirects
~~~~~~~~~

Refer to the `Apache Redirect directive documentation`_ for details.

``redirect_http``
  Optional, string.
  Redirect incoming requests on the HTTP port to the given URL.

``redirect_http_code``
  Optional, string/integer. Defaults to ``307`` (Temporary Redirect).
  Specify HTTP code used in the redirect response when redirecting to
  ``item.redirect_http``.

``redirect_https``
  Optional, string.
  Redirect incoming requests on the HTTPS port to the given URL.

``redirect_https_code``
  Optional, string/integer. Defaults to ``307`` (Temporary Redirect).
  Specify HTTP code used in the redirect response when redirecting to
  ``item.redirect_https``.

``redirect_to_https_with_code``
  Optional, string/integer. Defaults to ``301`` (Moved Permanently).
  Optional, string/integer. Specify HTTP code used in the redirect response from HTTP to
  HTTPS, by default 301 Moved Permanently.

``redirect_to_https``
  Optional, boolean. Defaults to :envvar:`apache__redirect_to_https`
  If ``True``, redirect connection from HTTP to the HTTPS version of the site.
  Set to ``False`` to allow to serve the website via HTTP and HTTPS and don't
  redirect HTTP to HTTPS.

HTTPS and TLS
~~~~~~~~~~~~~

``https_enabled``
  Optional, boolean. Defaults to :envvar:`apache__https_enabled`.
  Enable or disable HTTPS for this server configuration.

``tls_crt``
  Optional, string. Absolute path to a custom X.509 certificate to use. If not
  supplied, a certificate will managed by :ref:`debops.pki` will be used.

``tls_key``
  Optional, string. Absolute path to custom private key to use. If not
  supplied ``pki_key`` will be used instead.

``tls_dhparam_file``
  Optional, string. Absolute path to custom DHE parameters to use. If not
  supplied, :envvar:`apache__tls_dhparam_file` will be used instead.

``tls_cipher_suite_set_name``
  Optional, strings. Defaults to :envvar:`apache__tls_cipher_suite_set_name`.
  Set name of TLS cipher suites to use as defined in
  :envvar:`apache__tls_cipher_suite_sets`.

``pki_realm``
  Optional, string. Overwrites the default PKI realm used by Apache for this
  vhost configuration. See the :ref:`debops.pki` role for more information, as well
  as the :file:`/etc/pki/realms` directory on remote hosts for a list of
  available realms.

``pki_crt``
  Optional, string. Path to custom X.509 certificate to use, relative to the
  currently enabled PKI realm.

``pki_key``
  Optional, string. Path to custom private key to use, relative to the
  currently enabled PKI realm.

``ocsp_stapling_enabled``
  Optional, boolean. Defaults to :envvar:`apache__ocsp_stapling_enabled`
  Enable or disable OCSP Stapling.

``hsts_enabled``
  Optional, boolean. Defaults to ``True``. If this is set to ``True`` and HTTPS
  is enabled for this item, the `HTTP Strict Transport Security`_ header is set
  in the server's responses.  If this is set to ``False``, the header will not
  be set in the server's responses.

``hsts_preload``
  Optional, boolean. Defaults to :envvar:`apache__hsts_preload`.
  Add a "preload" parameter to the HSTS header which can be used with the
  https://hstspreload.appspot.com/ site to configure HSTS preloading for a
  given website.


.. _apache__ref_servers_http_security_headers:

HTTP security headers
~~~~~~~~~~~~~~~~~~~~~

``csp``
  Optional, string. Defaults to: ``default-src https: ;`` (force all assets to be loaded over HTTPS).
  Sets the first part of the ``Content-Security-Policy`` header.
  The string MUST end with a semicolon but MUST NOT begin with one.
  Make sure that you only use single quotes and no double quotes in the string.
  If no ``item.csp_report`` is given, it also determines the first part of the
  ``Content-Security-Policy-Report-Only`` header.
  Which headers are actually enabled is defined by ``item.csp_enabled``
  and ``item.csp_report_enabled``.
  Refer to the `Content Security Policy Reference`_.

``csp_report``
  Optional, string. This allows to set a different/potentially experimental
  ``Content-Security-Policy-Report-Only`` header than defined by ``item.csp``.

``csp_append``
  Optional, string. Defaults to: :envvar:`apache__http_csp_append`.
  CSP directives to append to all policies (``item.csp`` and ``item.csp_report``).
  This can be used to overwrite the default :envvar:`apache__http_csp_append` as needed.
  The string MUST end with a semicolon but MUST NOT begin with one.

``csp_enabled``
  Optional, boolean. Defaults to ``False``.
  If set to ``True`` and HTTPS is enabled for this item, the
  ``Content-Security-Policy`` header is set in server responses.

``csp_report_enabled``
  Optional, boolean. Defaults to ``False``.
  If this is set to ``True`` and HTTPS is enabled for this item, the
  ``Content-Security-Policy-Report-Only`` header is set in the server responses.

.. _apache__ref_vhost_http_xss_protection:

``http_xss_protection``
  Optional, string. Value of the ``X-XSS-Protection`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to :envvar:`apache__http_xss_protection`.

  ``1``
    Browsers should enable there build in cross-site scripting protection.

  ``mode=block``
    In case a cross-site scripting attack is detected, block the page from rendering.

    Note that the this option might create
    `a vulnerability in old versions of Internet Explorer
    <https://github.com/helmetjs/helmet#xss-filter-xssfilter>`.

  For more details and discussion see `What is the http-header
  “X-XSS-Protection”?
  <https://stackoverflow.com/questions/9090577/what-is-the-http-header-x-xss-protection>`_.

.. _apache__ref_vhost_http_referrer_policy:

``http_referrer_policy``
  Optional, string. Value of the ``Referrer-Policy`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to :envvar:`apache__http_referrer_policy`.
  Refer to `Referrer Policy`_ for more details. Note that this header is a
  draft as of 2016-10-11 but it is already supported by the majority of web
  browsers.


.. _apache__ref_vhost_apache_status:

Apache status
~~~~~~~~~~~~~

.. _apache__ref_vhost_status_enabled:

``status_enabled``
  Optional, boolean. Should the Apache server status be enabled?
  Defaults to :envvar:`apache__status_enabled`.

.. _apache__ref_vhost_status_location:

``status_location``
  Optional, string.
  The ``Location`` or URL path by which the Apache server status should be
  accessible.
  Defaults to :envvar:`apache__status_location`.

.. _apache__ref_vhost_status_allow_localhost:

``status_allow_localhost``
  Optional, boolean.
  Allow access to the Apache server status using the ``Require local``
  directive.
  Defaults to :envvar:`apache__status_allow_localhost`.

.. _apache__ref_vhost_status_directives:

``status_directives``
  Optional, string.
  Additional directives included into the ``Location`` sections for the Apache
  server status configuration. Can be used to customize access for example.
  Defaults to :envvar:`apache__status_directives`.

Type: raw
~~~~~~~~~

Available when ``item.type`` is set to ``raw``.
Don’t do all the fancy stuff that the normal templates can do for you and just
use the provided Apache configuration and dump it into the file.

``raw``
  Optional, string.
  Raw content to write into the virtual host configuration file.

Type: divert
~~~~~~~~~~~~

Available when ``item.type`` is set to ``divert``.
This special type does not create a virtual host file, instead it uses
:command:`dpkg-divert` to allow you to do a package management aware rename of a file.

Note that for this type no changes are done in they :file:`sites-enabled`
directory to avoid idempotency issues with a potential configuration with the same
filename as the configuration which is diverted away.

``divert_suffix``
  Optional, string. Defaults to ``.dpkg-divert``.
  Allows to change the suffix for the diverted file in the
  :file:`sites-available` directory.

``divert_filename``
  Optional, string. The default value is determined based on the values of
  ``item.name`` and ``item.filename``.
  Allows to change the divert filename.

``divert``
  Optional, string. Defaults to the file path determined for the virtual host configuration.
  Allows to specify a full file path where to divert the file to.
  Note that the ``item.divert_suffix`` is still in affect when using this option.

Examples
~~~~~~~~

Create virtual hosts for ``www.example.org`` and ``example.org``:

.. code-block:: yaml

   apache__host_vhosts:

     - name: [ 'www.example.org' ]
       root: '/srv/www/sites/www.example.org/public'

     - name: [ 'example.org' ]
       redirect_http: 'https://www.example.org'
       redirect_https: 'https://www.example.org'
       redirect_http_code: '301'
       redirect_https_code: '301'

The files under :file:`/srv/www/sites/www.example.org/public` are served for
requests against ``https://www.example.org``.
Requests against ``example.org`` are permanently redirected to the canonical
``www.example.org`` site.
HTTPS is the default and legacy HTTP connection attempts are permanently
redirected to HTTPS. HSTS_ tells clients to only connect to the site using
HTTPS from now on. Certificates managed by :ref:`debops.pki` are used according to
the ``name`` of the virtual host which should match a PKI realm of :ref:`debops.pki`.
