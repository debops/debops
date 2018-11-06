Default variable details
========================

Some of ``debops.icinga`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _icinga__ref_configuration:

icinga__configuration
---------------------

The ``icinga__*_configuration`` variables specify the contents of the Icinga
2 configuration located in the :file:`/etc/icinga2/` directory. The variables
are combined together using the :envvar:`icinga__combined_configuration`
variable, which means that users don't need to copy entire values to the
inventory to change it.

Because Icinga 2 configuration language is extensive, the role is focused only
on conditional activation of the specific files and sections inside. You will
want to read the `upstream documentation`__ to learn how to configure Icinga
2 using its DSL.

.. __: https://www.icinga.com/docs/icinga2/latest/doc/04-configuring-icinga-2/

The vriables contain lists of YAML dictionaries, each dictionary can be defined
using specific parameters:

``name``
  Required. The name of the file located in the :file:`/etc/icinga2/`
  directory, for example ``icinga2.conf``. This can also include
  subdirectories, for example ``conf.d/templates.conf``. Missing subdirectories
  will be automatically created by the role.

  This parameter is used as a handle for merging multiple configuration entries
  together.

``filename``
  Optional. Alternative filename with optional subdirectories. Can be used to
  override the filename specified in the ``name`` parameter. Usually not used.

``divert``
  Optional, boolean. When defined and ``True``, this parameter marks the file
  as belonging to a ``.deb`` package. The original file will be diverted or
  reverted depending on the ``state`` parameter to allow for unobtrusive
  package upgrades. Diverted files have ``.dpkg-divert`` suffix and are ignored
  by Icinga 2.

``state``
  Optional. Specify the desired state of a given configuration file. Possible
  states:

  - ``present``: default if not defined. The configuration file will be
    generated, any original files will be diverted to preserve them.

  - ``absent``: the file will be removed. Any diverted files will be returned
    to their original state.

  - ``init``: the configuration of a given file will be primed, but will not be
    actually implemented by the role. This can be used to prepare configuration
    files to be activated conditionally.

  - ``ignore``: a given configuration entry will be ignored during template
    generation. This can be used to disable specific configuration entries
    conditionally.

  - ``divert``: only divert a given configuration file without generating
    a custom one. The files will be reverted back when the state is set to
    ``absent``.

  - ``feature``: only enable/disable the feature state in the
    :file:`/etc/icinga2/features-enabled/` directory.

``feature_name``
  Optional. Specify name of the symlink managed in the
  :file:`/etc/icinga2/features-enabled/` directory, without the ``.conf``
  suffix. This should be only used with configuration files located in the
  :file:`features-available/` subdirectory, otherwise the generated symlinks
  will be broken.

  The ``name`` parameter is not correlated with the ``feature_name``, and is
  used only for configuration merging.

``feature_state``
  Optional. If set and ``present``, the symlink to a particular feature file
  will be created. If ``absent``, the symlink to a particular feature will be
  removed, thus disabling it.

``owner``
  Optional. Specify the UNIX account owner of the configuration file. If not
  specified, ``root`` will be the owner.

``group``
  Optional. Specify the UNIX group of the configuration file. If not specified,
  ``root`` will be the group.

``mode``
  Optional. Specify the file attributes. If not specified, ``0644`` will be
  used by default.

``no_log``
  Optional, boolean. If set and ``True``, Ansible will not log the generation
  of a given configuration file. This might be useful for files with sensitive
  data like passwords.

``comment``
  Optional. String or YAML text block with a comment, included in the beginning
  of the configuration file.

``value``
  Optional. String or YAML text block that contains the Icinga 2 configuration,
  specified using `Icinga 2 DSL`__. It will be included in the configuration
  file as-is.

  .. __: https://www.icinga.com/docs/icinga2/latest/doc/17-language-reference/

``options``
  Optional. List of configuration snippets that will be included in the file.
  It's an alternative to a single ``value`` entry which can be used to
  conditionally enable or disable parts of the configuration file. Options
  lists from different configuration entries are merged together and can affect
  each other.

  Each list element is a YAML dictionary with specific parameters:

  ``name``
    An element identifier, it is used for merging ``options`` lists from
    different configuration entries and is ignored otherwise. It should be an
    unique string.

  ``value``
    Required. String or YAML text block with Icinga 2 configuration written in
    is DSL. Will be included as-is in the configuration file.

  ``comment``
    Optional. String or YAML text block with a comment which will be added
    before a given element.

  ``state``
    Optional. If not set or ``present``, the configuration option will be
    included in the generated file. If ``absent``, the configuration option
    will not be included in the generated file. If ``ignore``, a given list
    element is not evaluated by Ansible and will be ignored. If ``comment``,
    the configuration option will be included in the configuration file, but
    commented out.

  ``weight``
    Optional. A positive or negative number that affects the order of the
    elements in the options list. It can be used to move configuration lower or
    higher in the configuration file.

Examples
~~~~~~~~

Many examples can be found in the role :file:`defaults/main.yml` file.

Add simple host checks in separate directory:

.. code-block:: yaml

   icinga__configuration:

     - name: 'conf.d/hosts/host1.{{ ansible_domain }}/host.conf'
       comment: 'Custom host configuration'

       options:

         - name: 'host'
           value: |
             object Host "host1.{{ ansible_domain }}" {
               address = "host1.{{ ansible_domain }}"
               check_command = "hostalive"
             }
           state: 'present'

     - name: 'conf.d/hosts/host2.{{ ansible_domain }}/host.conf'
       value: |
         object Host "host2.{{ ansible_domain }}" {
           address = "host2.{{ ansible_domain }}"
           check_command = "hostalive"
         }
       state: 'present'

Define a set of services and apply them to hosts in a specific zone:

.. code-block:: yaml

   icinga__configuration:

     - name: 'zones.d/master/services.conf'
       state: 'present'
       options:

         - name: 'service_load'
           value: |
             apply Service "load" {
               import "generic-service"
               check_command = "load"
               command_endpoint = host.vars.client_endpoint
               assign where host.vars.client_endpoint
             }
           state: 'present'

         - name: 'service_procs'
           value: |
             apply Service "procs" {
               import "generic-service"
               check_command = "procs"
               command_endpoint = host.vars.client_endpoint
               assign where host.vars.client_endpoint
             }
           state: 'present'

     - name: 'zones.d/master/host1.{{ ansible_domain }}.conf'
       options:

         - name: 'object_zone'
           value: |
             object Zone "host1.{{ ansible_domain }}" {
               endpoints = [ "host1.{{ ansible_domain }}" ]
               parent = "master"
             }
           state: 'present'

         - name: 'object_endpoint'
           value: |
             object Endpoint "host1.{{ ansible_domain }}" {
               host = "host1.{{ ansible_domain }}"
             }
           state: 'present'

         - name: 'object_host'
           value: |
             object Host "host1.{{ ansible_domain }}" {
               import "generic-host"
               address = "host1.{{ ansible_domain }}"
               vars.notification["mail"] = {
                 groups = [ "icingaadmins" ]
               }
               vars.client_endpoint = name
             }
           state: 'present'


.. _icinga__ref_custom_files:

icinga__custom_files
--------------------

The ``icinga__*_custom_files`` variables can be used to copy additional hosts
to hosts managed with the ``debops.icinga`` role. The variables are lists, each
list entry is a YAML dictionary with specific parameters:

``content``
  String or YAML text block with file contents. Cannot be set with the ``src``
  parameter at the same time.

``src``
  Absolute path to the file located on the Ansible Controller which will be
  copied to the remote host. Cannot be set with the ``content`` parameter at
  the same time.

``dest``
  Required. Absolute path where the file will be placed on the remote host.

``owner``
  Optional. Specify the owner of the file. If not specified, ``root`` will be
  the owner.

``group``
  Optional. Specify the default group of the file. If not specified, ``root``
  will be the default group.

``mode``
  Optional. Specify the file attributes. If not specified, ``0755`` will be set
  (by default the role assumes that the managed custom files are scripts).

``force``
  Optional, boolean. If ``True`` (default), the role will override already
  existing file. If ``False``, the role will not override an existing file.

``state``
  Optional. If not set or ``present``, the file will be copied to the remote
  host. This can be used to conditionally copy files depending on other
  factors.

Examples
~~~~~~~~

Add a simple hello world script in Icinga 2 :file:`scripts/` directory:

.. code-block:: yaml

   icinga__custom_files:
     - content: |
         #!/bin/sh

         echo "Hello, world!"
       dest: '/etc/icinga2/scripts/hello-world.sh'
