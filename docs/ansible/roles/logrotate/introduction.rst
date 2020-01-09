Introduction
============

The ``logrotate`` package is used to periodically rotate logs, so that they
don't fill up the disk space on the filesystem. Rotated logs can be moved to
a different host or emailed before removal for archival purposes.

The ``debops.logrotate`` Ansible role allows you to manage log rotation
configuration for system packages, or create custom log configuration. The role
can be used by other roles as a dependency to make automatic ``logrotate``
configuration easier.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run::

    ansible-galaxy install debops.logrotate

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
