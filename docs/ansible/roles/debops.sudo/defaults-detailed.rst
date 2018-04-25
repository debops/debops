Default variable details
========================

Some of ``debops.sudo`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _sudo__ref_sudoers:

sudo__sudoers
-------------

The ``sudo__*_sudoers`` variables define :command:`sudo` configuration located
in :file:`/etc/sudoers.d/` directory. Each variable is a list of YAML
dictionaries, with specific parameters:

``name``
  Required. Name of the configuration section, used as a filename, and as
  a marker which merges multiple configuration entries together.

``filename``
  Optional. Set custom filename for a given configuration file, located in
  :file:`/etc/sudoers.d/` directory.

``comment``
  Optional. A string or YAML text block with comments added at the beginning of
  the configuration file.

``state``
  Optional. If not defined or ``present`` (default), the configuration file
  will be generated. If ``absent``, the configuration file will be removed.

  If ``init``, the configuration for a given entry will be prepared but not
  actually present on the host. It can be activated conditionally in a later
  entry.

  If ``ignore``, a given configuration entry will not be evaluated by the role.

``raw``
  Optional. A string or YAML text block with :man:`sudoers(5)` configuration
  added at the end of the configuration file as-is.

``options``
  Optional. A list of :man:`sudoers(5)` configuration snippets specified as
  YAML dictionaries. Each dictionary can have specific parameters:

  ``name``
    Required. Name of a configuration section, only used as a handle for
    merging options from multiple configuration entries.

  ``value``
    Required. A string or YAML text block that contains the :man:`sudoers(5)`
    configuration snippet. Values from different configuration entries will be
    merged into one list and present in the configuration file.

  ``comment``
    Optional. A string or YAML text block with a comment about a given option.

  ``weight``
    Optional. A positive or negative number which influences the order in which
    the entries will be present in the configuration file. The lower the
    number, the higher in the file a given option will be present.

  ``state``
    Optional. If not defined or ``present``, a given configuration option will
    be added in the configuration file. If ``absent``, a given option will be
    removed from the configuration file.

Examples
~~~~~~~~

Allow user ``ray`` on host ``rushmore`` to run specific commands with elevated
privileges without password confirmation:

.. code-block:: yaml

   sudo__sudoers:

     - name: 'ray-nopasswd-commands'
       raw: |
         ray   rushmore = NOPASSWD: /bin/kill, /bin/ls, /usr/bin/lprm

Override some of the built-in defaults conditionally:

.. code-block:: yaml

   sudo__sudoers:

     - name: '00-defaults-override'
       options:

         - name: 'syslog-auth'
           comment: 'Log events to syslog via "auth" facility'
           value: 'Defaults    syslog=auth'

         - name: 'disable-lecture'
           comment: "Don't show the default lecture on specific hosts"
           value: |
             Defaults    !lecture
           state: '{{ "present"
                      if (ansible_hostname == 'bastion')
                      else "absent" }}'

On the contrary, don't create the above defaults file when a host is in
a specific Ansible inventory group:

.. code-block:: yaml

   sudo__group_sudoers:

     - name: '00-defaults-override'
       state: 'absent'
