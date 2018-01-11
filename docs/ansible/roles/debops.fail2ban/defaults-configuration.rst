Default variables: configuration
================================

some of ``debops.fail2ban`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _fail2ban_actions:

fail2ban_actions
----------------

List of local ``fail2ban`` actions that should be present or absent when configuring
``fail2ban``. Each action is defined as a YAML dict with the following keys:

``name``
  Required. Name of the filter.

``ban``
  Required. Command executed when banning an IP. Take care that the command is executed
  with ``fail2ban`` user rights.

``check``
  Optional. Command executed once before each ``ban`` command.

``filename``
  Optional. Alternative name of the action configuration file.

``start``
  Optional. Command executed once at the start of ``fail2ban``.

``state``
  Optional. If ``present``, the action will be created when configuring ``fail2ban``.
  If ``absent``, the action will be removed when configuring ``fail2ban``.

``stop``
  Optional. Command executed once at the end of ``fail2ban``.

``unban``
  Optional. Command executed when unbanning an IP. Take care that the command is executed
  with ``fail2ban`` user rights.

.. _fail2ban_filters:

fail2ban_filters
----------------

List of local ``fail2ban`` filters that should be present or absent when configuring
``fail2ban``. Each filter is defined as a YAML dict with the following keys:

``name``
  Required. Name of the filter.

``after``
  Optional. Specify an additional filter configuration file that ``fail2ban`` will
  read after reading this filter configuration filer.

``before``
  Optional. Specify an additional filter configuration file that ``fail2ban`` will
  read before reading this filter configuration file.

``definitions``
  Optional. Custom definitions used by the filter.

``failregex``
  Required. A string of regular expression(s) used by the filter to detect 
  break-in attempts. You can have the filter try to match multiple regular 
  expressions by using the ``|`` character (the YAML literal style operator). Each 
  regular expression should be on its own line. Refer to the `examples`_ section.

``filename``
  Optional. Alternative name of the filter configuration file. If not specified, it
  will use the ``name`` of the filter.

``ignoreregex``
  Optional. Regular expression(s) used to filter out invalid break-in attempts. You
  can have the filter try to match multiple regular expressions. Each regular
  expression should be on its own line.

``state``
  Optional. If ``present``, the filter will be created when configuring ``fail2ban``.
  If ``absent``, the filter will be removed when configuring ``fail2ban``.

Refer to the ``fail2ban`` `filter wiki`_ for more information.

.. _filter wiki: https://www.fail2ban.org/wiki/index.php/MANUAL_0_8#Filters

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

.. _examples:

Examples:
~~~~~~~~~

**Jails**

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

**Filters**

Add custom local filter ``web-auth`` with multiple ``failregex`` rules::

    fail2ban_filters:
      - name: web-auth
        failregex: |
          Authentication failure for .* from <HOST>
          Failed [-/\w]+ for .* from <HOST>
          ROOT LOGIN REFUSED .* FROM <HOST>
        state: present

Add custom local filter ``root-auth`` with a single ``failregex`` rule::

    fail2ban_filters:
      - name: root-auth
        failregex: 'Authentication failure for .* from <HOST>'
        state: present

