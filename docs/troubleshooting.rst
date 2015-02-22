Troubleshooting
===============

In case of any errors during backup, ``debops.rsnapshot`` role collects output
of all scripts and sends it if anything shows up to ``<backup>`` e-mail
account. With default `debops.postfix`_ configuration, this account is aliased
to ``root`` account, so all e-mails should be forwarded to the system
administrator.

.. _debops.postfix: https://github.com/debops/ansible-postfix/

Logs for each server configuration are stored in ``/var/log/rsnapshot/``
directory, and are automatically rotated.

