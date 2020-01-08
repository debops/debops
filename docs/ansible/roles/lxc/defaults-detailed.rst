Default variable details
========================

Some of ``debops.lxc`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1


.. _lxc__ref_configuration:

lxc__configuration
------------------

The ``lxc__*_configuration`` variables define the contents of the configuration
files in the :file:`/etc/lxc/` directory.

Examples
~~~~~~~~

Select the default bridge interface used by new unprivileged LXC containers:

.. code-block:: yaml

   lxc__configuration:

     - name: 'unprivileged'
       options:
         - 'lxc.network.link': 'br0'

Change the default LXC configuration file used to generate LXC containers to
unprivileged:

.. code-block:: yaml

   lxc__configuration:

     - name: 'lxc'
       options:

         - name: 'lxc.default_config'
           value: '/etc/lxc/unprivileged.conf'

The same change, written as a simple YAML dictionary:

.. code-block:: yaml

   lxc__configuration:

     - name: 'lxc'
       options:
         - 'lxc.default_config': '/etc/lxc/unprivileged.conf'

Syntax
~~~~~~

Each variable is a list of YAML dictionaries, each dictionary can contain
specific parameters:

``name``
  Required. Name of the configuration file, saved as
  :file:`/etc/lxc/<name>.conf`. This parameter is also used as a key while
  merging multiple configuration entries.

  Please note that the ``lxc`` package creates the
  :file:`/etc/lxc/default.conf` configuration file. This file is not managed by
  the :ref:`debops.lxc` role and it's best not to overwrite it so that package
  upgrades don't have issues. In other words, don't use the ``default`` as the
  name of the configuration file.

``filename``
  Optional. Custom filename of the specified configuration. You need to include
  the ``.conf`` prefix in the filename.

``state``
  Optional. Specify desired state of a given configuration file. Possible
  states:

  - ``present`` or not specified: the file will be generated.

  - ``absent``: the file will be removed if it exists, otherwise it won't be
    generated.

  - ``ignore``: A given configuration entry will be ignored by the role.

``comment``
  Optional. A string or YAML text block with a comment added at the top of the
  configuration file.

``raw``
  Optional. A string or YAML text block with LXC configuration, which will be
  added as-is at the end of the configuration file.

``options``
  Optional. A YAML list of LXC configuration options defined as YAML
  dictionaries. Each dictionary key is an ``lxc.*`` configuration key, and the
  dictionary is the configuration value, defined as a string. The ``options``
  lists from multiple configuration entries with the same ``name`` will be
  merged together.

  If the dictionary has ``name`` and ``value`` keys, a given dictionary is
  interpreted with specific parameters:

  ``name``
    The LXC configuration option. It's used as a key to merge configuration
    options. If your configuration uses the same configuration options multiple
    times, you need to differentiate each one, for example with a prefix or
    suffix.

  ``alias``
    Optional. An alternative option name which will be used in the
    configuration file. This can be used to allow multiple LXC options with the
    same name.

  ``value``
    The value of an LXC configuration option, a string or a YAML list of
    strings which will joined with spaces.

  ``comment``
    Option. a string or a YAML text block with a comment added to a given LXC
    configuration option.

  ``separator``
    Optional, boolean. If ``True``, a blank line will be added before the
    option. It can be used to separate configuration into sections for better
    readability.

  ``state``
    Optional. Set a custom state for a given LXC configuration option. Known
    states:

    - ``present`` or not specified: the option will be present in the generated
      configuration file.

    - ``absent``: the option will not be present in the generated configuration
      file.

    - ``comment``: the option will be present, but commented out.

    - ``ignore``: a given entry will be ignored during configuration file
      generation.


.. _lxc__ref_containers:

lxc__containers
---------------

THe :envvar:`lxc__containers` variable can be used to define and manage LXC
containers on a given LXC host. By default, DebOps configures LXC containers
with static MAC addresses based on the container name, therefore the names used
for LXC containers should be unique on a given subnet, even between different
LXC hosts.

Examples
~~~~~~~~

Create a few LXC containers using defaults - unprivileged LXC container based
on the LXC host OS distribution, release and architecture, with SSH support
enabled:

.. code-block:: yaml

   lxc__containers:

     - 'smtp'
     - 'database'
     - 'webserver'

Remove some of the existing LXC containers from a host:

.. code-block:: yaml

   lxc__containers:

     - name: 'smtp'
       state: 'absent'

     - name: 'webserver'
       state: 'absent'

Create an LXC container using specific OS distribution and release, without SSH
access configured inside the container:

.. code-block:: yaml

   lxc__containers:

     - name: 'mail-server'
       distribution: 'ubuntu'
       release: 'bionic'
       ssh: False

Create a privileged LXC container using ``lxc-debian`` LXC template with
overridden template options:

.. code-block:: yaml

   lxc__containers:

     - name: 'privileged'
       config: '/etc/lxc/privileged.conf'
       template: 'debian'
       template_options: ''

Create custom directory on LXC host and share it between two unprivileged LXC
containers using the :ref:`debops.resources` and :ref:`debops.lxc` roles,
mounted at :file:`/opt` directory inside of the containers:

.. code-block:: yaml

   resources__host_paths:

     - name: '/srv/shared/lxc-opt'
       state: 'directory'
       owner: '100000'
       group: '100000'
       mode: '0755'

   lxc__containers:

     - name: 'container1'
       fstab: |
         /srv/shared/lxc-opt opt none bind 0 0
       state: 'started'

     - name: 'container2'
       fstab: |
         /srv/shared/lxc-opt opt none bind 0 0
       state: 'started'

Syntax
~~~~~~

The variable contains a list of LXC container names, or (as the extended
format) YAML dictionaries, each dictionary defines a aprticular LXC container
using specific parameters.

The parameters listed below correspond to the `lxc_container`__ Ansible module
parameters. See its documentation for details. Most common parameters used to
manage LXC containers are:

.. __: https://docs.ansible.com/ansible/devel/modules/lxc_container_module.html

``name``
  Required. Name of an LXC container to manage. The names should be unique
  across all LXC hosts connected to the same subnet. The ``lxc-hwaddr-static``
  LXC hook configured by DebOps will generate random, but predictable MAC
  addresses based on the container name.

``state``
  Optional. If not specified or ``started``, the LXC container will be created
  and started. On initial creation, if ``started`` is specified explicitly, the
  role will restart the LXC container to use the static MAC addresses generated
  by the "pre-start" LXC hook.

  If ``absent``, the role will remove an existing LXC container.

  If ``stopped``, the existing LXC container will be stopped, if already
  running.

  If ``restarted``, the container will be restarted on the next execution of
  the role.

  If ``frozen``, the LXC container will be frozen on the next execution of the
  role.

``config``
  Optional. Absolute path to the LXC system configuration file which will be
  used to create the LXC container. If not specified, the configuration file
  defined in :envvar:`lxc__default_container_config` variable will be used.

``container_command``
  Optional. A String or YAML text block with a command or a shell script to
  execute inside of the LXC container after it's started.

``template``
  Optional. Name of the LXC template to use for creating a given LXC container,
  for example ``download``, ``debian``, ``ubuntu``.  If not specified, the
  value of :envvar:`lxc__default_container_template` variable will be used. You
  can find available LXC templates in the :file:`/usr/share/lxc/templates/`
  directory on the LXC host.

``template_options``
  Optional. A string with shell arguments passed to the template script. If not
  specified, arguments suitable for the ``lxc-download`` LXC template will be
  automatically generated based on the LXC host OS distribution, release and
  architecture. To override the automatic creation of arguments, specify an
  empty string.

The parameters below can be used to configure additional aspects of the LXC
containers when managed by the :ref:`debops.lxc` Ansible role:

``fstab``
  Optional. YAML text block with :man:`fstab(5)` configuration to mount
  filesystems inside of the LXC containers. If this parameter is specified, the
  role will create the :file:`/var/lib/lxc/<container>/fstab` file with the
  contents of this parameter and configure the container to mount the
  filesystems specified in this file. Existing LXC containers are not modified.

  See the :man:`lxc.container.conf(5)` ``lxc.mount`` option documentation for
  more details.

``ssh``
  Optional, boolean. If ``True``, the role will use the
  :command:`lxc-prepare-ssh` script to configure SSH access and authorized keys
  in a given LXC container. This will be done only at container creation time.

  If ``False``, the role will not configure SSH access inside of the container.
  It can still be accessed via :command:`lxc-attach` command; Ansible can use
  the ``lxc`` connection plugin locally, or ``lxc_ssh`` connection plugin
  remotely to configure the container without SSH access.

  If not specified, the value of :envvar:`lxc__default_container_ssh` will
  determine the SSH status.

``systemd_override``
  Optional. YAML text block that contains :command:`systemd` unit configuration
  for a particular LXC container instance. If specified, the configuration will
  be added or removed depending on the LXC container state. When the
  :command:`systemd` configuration is changed, the LXC container will be
  restarted.

``distribution``
  Optional. Specify the name of the OS distribution to use with the
  ``lxc-download`` LXC template. If not specified, the
  :envvar:`lxc__default_container_distribution` value will be used.

``release``
  Optional. Specify the name of the OS release to use with the ``lxc-download``
  LXC template. If not specified, the :envvar:`lxc__default_container_release`
  value will be used.

``architecture``
  Optional. Specify the name of the host architecture to use with the
  ``lxc-download`` LXC template. If not specified, the
  :envvar:`lxc__default_container_architecture` value will be used.

You can run the command:

.. code-block:: console

   lxc-create -n container -t download -- -l

to see the list of available unprivileged LXC container images, with
distribution, release and architecture combinations.
