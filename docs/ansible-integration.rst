Ansible integration and role design
===================================

* Try not to modify/replace configuration files which are maintained by Debian.
  In particular the :file:`/etc/apache2/apache2.conf` is not altered.
* The ``IfVersion`` directive is not used to keep the number of enabled modules
  as minimum as possible. Instead the configuration is generated for the
  currently detected Apache version.
* Most variables which directly correspond to a Apache directive are not masked
  or otherwise changed (for example allowing ``True``, ``False`` for directives
  which expect ``on``, ``off``).
  Together with the direct reference to upstream documentation provided in the
  role documentation this is expected to provide more transparency to the user
  and allow the role to be future proof when changes occurrence upstream.
* For directives where ``off`` or ``False`` might be a valid option, the
  special variable ``omit`` (use in Jinja: ``{{ omit }}``) is intended to be
  used when the directive should be omitted.
