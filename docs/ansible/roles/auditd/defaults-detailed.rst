.. Copyright (C) 2026 seven-beep <github@soulintheshell.com>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``auditd`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. _auditd__ref_rules:

auditd__rules
-------------

The ``auditd__*_rules`` variables defines the set of :program:`auditd` rules
files that should be wrote in :file:`/etc/auditd/rules.d`.

Syntax
~~~~~~

The variables are lists of YAML dictionaries, each dictionary defines a rule
file, and should contains a rule key that will hold the actual rules
definitions.

``name``
  Required, string. This will be used to construct the filename (name + .rules)
  of the rule file if the filename entry is not defined.

``filename``
  Optional, string. This can be used as raw base filename. It should end with
  .rules to be considered by :program:`auditd`.

``comment``
  Optional, string. This will be commented as header of the rule file.

``rules``
  Optional, list of dictionaries. Defines the rules present in a given
  rule file. You can use the parameters:


     ``name``
       Required, string. The name is used to identify rules and merge them. It
       is not used in the final rule file.

     ``raw``
       Optional, string. Raw :program:`auditd` rules. This can be used by
       example for ``-w`` rules or other specific arguments that cannot be
       interpreted by the ``rules`` list,

     ``append``
       Optional, boolean. Default to True. Whether the rule should be appended
       *(-a)* or prepended *(-A)*.

     ``list``
       Optional, string. Default to ``exit``. See ``man auditctl`` for valid
       list names

     ``action``
       Optional, string. Default to ``always``. Valid options are ``always`` and
       ``never``.

     ``fields``
       Optional, list of strings. Build a rule field: name, operation,
       value.

       The string ``*uid_min*`` can be used in the ``fields`` parameter and will
       be replaced by the minimal UID of users *(it is usually 1000, defined in
       /etc/login.defs)*.

     ``comparison``
       Optional, list of strings. Build an inter-field comparison rule: field,
       operation, field.

     ``syscalls``
       Optional, list of strings. Any syscall name or number, if not specified,
       all syscalls will be audited.

     ``permissions``
       Optional, string. Permission filter for file operations.

     ``keys``
       Optional, list of strings. Set a filter key on an audit rule.

     ``paths``
       Optional, string or list of strings. This is convenience parameter that
       will populate the path fields of the rule, eg: ``['/path/to/path1',
       '/path/to/file2']`` will be transformed into ``-F path=/path/to/file1 -F
       path=/path/to/file2``.

     ``dirs``
       Optional, string or list of strings.  This is convenience parameter that
       will populate the dir fields of the rule, eg: ``['/path/to/dir1',
       '/path/to/dir2']`` will be transformed into ``-F dir=/path/to/dir1, -F
       dir=/path/to/dir2``
