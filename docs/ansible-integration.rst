Ansible integration and role design
===================================

.. include:: includes/all.rst

Design goals
------------

* Try not to modify/replace configuration files which are maintained by Debian.
  In particular the :file:`/etc/apache2/apache2.conf` is not altered.
* The ``IfVersion`` directive is not used to keep the number of enabled modules
  as minimum as possible. Instead the configuration is generated for the
  currently detected Apache version.
* Most variables which directly correspond to a Apache directive are not masked
  or otherwise changed (for example using ``True``, ``False`` for directives
  which expect ``on``, ``off`` is *not* supported).
  Together with the direct reference to upstream documentation provided in the
  role documentation this is expected to provide more transparency to the user
  and allow the role to be future proof when changes occur upstream.
* For directives where ``off`` or ``False`` might be a valid option, the
  special variable ``omit`` (use in Jinja: ``{{ omit }}``) is intended to be
  used when the directive should be omitted (not written to the Apache
  configuration at all).


Alternative roles
-----------------

Has `Ansible Galaxy`_ an impressive number of Ansible roles for Apache to your
disposal. A few of them have been checked out before/while writing this role:

* `geerlingguy.apache <https://github.com/geerlingguy/ansible-role-apache>`_
* `jpnewman.apache <https://github.com/jpnewman/ansible-role-apache>`_
* And peeked at a few more.

However, none of the already existing roles where found to be a suitable start for
Apache support in Debops so this role has been designed and written from scratch.
Unfortunately, that workflow is not uncommon considering the quality requirements and standards of DebOps.
