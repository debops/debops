Description
===========

The :file:`/etc/aliases` file contains the mail alias database used by the
various SMTP daemons to redirect local mail to remote recipients, local files,
commands, etc. See the :man:`aliases(5)` for more details.

This role can be used to set the contents of the alias database, either using
Ansible inventory variables, or as a dependency of another Ansible role.
