Default variables: configuration
================================

some of ``debops.fail2ban`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _fail2ban_jails:

fail2ban_jails
--------------

Jails are defined in the form of dicts, where dict keys are the option names
and dict values are option values. You can specify values either as strings or
YAML lists, in which case elements of the list will be separated by commas.

Some keys have a special meaning:

``name``
  Jail name, used as a section header and part of the filename. Required.

``filename``
  Alternative file name, optional.

``comment``
  A commented text added before the given jail

``delete``
  If this option is present and ``True``, file which defines a given jail will
  be deleted

``ignoreip``
  **List** of IP addresses or CIDR subnets which should be ignored by
  ``fail2ban``

``action``
  It should be a name of a default or custom action, which will be used by
  ``fail2ban``

Other options are the same as normal ``fail2ban`` jail configuration options.
Refer to default ``/etc/fail2ban/jail.conf`` or `fail2ban wiki`_ for possible
options.

.. _fail2ban wiki: http://www.fail2ban.org/wiki/index.php/MANUAL_0_8#Jails

Examples:
~~~~~~~~~

Enable ``ssh`` jail and configure it to send mail messages about banned hosts::

    fail2ban_jails:

      - name: 'ssh'
        enabled: 'true'
        action: 'action_mw'

Enable ``dovecot`` jail with custom filename and send mail notifications to
postmaster::

    fail2ban_jails:

      - name: 'dovecot'
        filename: '50_dovecot'
        enabled: 'true'
        destemail: 'postmaster@{{ ansible_domain }}'

