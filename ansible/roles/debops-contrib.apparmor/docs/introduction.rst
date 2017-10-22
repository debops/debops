Introduction
============

.. include:: includes/all.rst

AppArmor is able to restrict what programs can do and access based on policies
for those programs.

See `AppArmor in the Debian Wiki <https://wiki.debian.org/AppArmor/HowToUse>`_.

By default (e. g. no auditd_ installed) log messages from AppArmor are logged
via syslog to the kernel facility which usually ends up under
:file:`/var/log/kern.log`.

.. _auditd: https://packages.debian.org/search?keywords=auditd


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.3``. To install it, run::

    ansible-galaxy install debops-contrib.apparmor

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
