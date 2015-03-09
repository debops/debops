.. _DebOps configuration:

Configuration
=============

**Note** You do not need to configure anything to run DebOps.

DebOps reads configuration files at several places. All configurations
files found are merged and the values read later take precedence.

Windows:

- ``%APPDATA%\debops.cfg`` (with ``%APPDATA%`` defaulting to ``~\Application Data``)

- ``project-dir\.debops.cfg``

MacOS X:

- ``~/Library/Application Support/\debops.cfg``
- ``project-dir/.debops.cfg``

All others (including Linux):

- ``/etc/debops.cfg``

- in each directory of ``$XDG_CONFIG_DIRS``: ``dir/debops.cfg``

- ``$XDG_CONFIG_HOME/debops.cfg``

- ``project-dir/.debops.cfg``


Configuration options
---------------------

``debops.cfg`` configuration file is an `INI file`_ similar to ``ansible.cfg``.

.. _INI file: https://en.wikipedia.org/wiki/INI_file

The ``[paths]`` section
~~~~~~~~~~~~~~~~~~~~~~~

``data-home``
  Default "home directory" of the DebOps playbooks and roles, all main paths
  are relative to this one.

  Default values:

  - Linux: ``$XDG_DATA_HOME/debops/``

  - MacOS X: ``~/Library/Application Support/debops/``

  - MS Windows: ``%APPDTA%\debops``

``install-path``
  Indicates where DebOps playbooks and roles are installed.

  Default value: ``%(data-home)s/debops-playbooks``

``playbooks-paths``
  List of comma-separated paths where playbooks can be found. ``debops`` script
  will search these paths looking for playbooks to execute.

  Default value: ``%(install-path)s/playbooks``

``template-paths``
  List of comma-separated paths where ``template_src`` lookup plugin will look
  for custom templates (alternative ``templates/`` directories). You can use
  this to override templates provided with official roles (when supported).

  Default value: none

``file-paths``
  List of comma-separated paths where ``file_src`` lookup plugin will look for
  custom files (alternative ``files/`` directories). You can use this to
  override files provided with official roles (when supported).

  Default value: none


The ``[ansible <section>]`` sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each configuration section in the form ``[ansible <section>]`` will be written
into generated ``ansible.cfg`` configuration file, into a corresponding
``[section]``. This way you can configure Ansible depending on the project
directory. For example, to set custom ``{{ ansible_managed }}`` string, you can
use::

    [ansible defaults]
    ansible_managed = Custom string

Example ``debops.cfg`` configuration file
-----------------------------------------

This file is created by ``debops-init`` command in the specified project directory::

    [paths]
    ;data-home: /opt/debops

    [ansible defaults]
    ;callback_plugins = /my/plugins/callback
    ;roles_path = /my/roles

    [ansible paramiko]
    ;record_host_keys=True

    [ansible ssh_connection]
    ;ssh_args = -o ControlMaster=auto -o ControlPersist=60s



..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
