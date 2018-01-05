.. _libvirtd_qemu__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.libvirtd_qemu`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _libvirtd_qemu__ref_configuration:

libvirtd_qemu__configuration
----------------------------

The ``libvirtd_qemu__*_configuration`` variables are YAML lists which define
the contents of the :file:`/etc/libvirt/qemu.conf` configuration file. The
lists are parsed by the template in order defined by the
:envvar:`libvirtd_qemu__combined_configuration` variable, which allows
modification of the parameters defined in earlier lists by the latter ones.

Each element of the list is a YAML dictionary. The dictionary can specify
:command:`qemu` configuration parameters as dictionary keys and they values as
dictionary values:

.. code-block:: yaml

   libvirtd_qemu__configuration:

     - 'min_workers': 5
       'max_workers': 20

     - 'unix_sock_group':    'libvirt'
       'unix_sock_ro_perms': '0770'
       'unix_sock_rw_perms': '0770'

Parameters specified in this way will automatically be configured as "present"
in the configuration file to override any "comment" state (see below).

Alternatively, each YAML dictionary can contain a ``name`` key, which tells the
role to interpret a given dictionary using specific parameters:

``name``
  Required. Name of the parameter to manage. Parameter names can contain
  alphanumeric characters and an underscore (``_``) character. See the
  :file:`/etc/libvirt/qemu.conf` configuration file for a list of known
  parameters and their meaning.

``state``
  Optional. If not specified or ``present``, the parameter will be present in
  the configuration file. If ``absent``, the parameter will not be included in
  the generated configuration file. If ``comment``, the parameter will be
  commented out in the configuration file. If ``ignore``, a given YAML
  dictionary will not be evaluated.

``comment``
  Optional. String or a YAML dictionary with a comment for a particular
  parameter.

``value``
  Optional. Specify the value of a given parameter. Values can be booleans,
  numbers, quoted strings or YAML lists of strings; empty variants work as
  well. If value parameter is not specified, an empty string will be set and
  the parameter will be automatically quoted.

``section``
  Optional. Specify the name of the section of the configuration file in which
  the parameter should be placed. Section names and their order are defined in
  the :envvar:`libvirtd_qemu__configuration_sections` variable. If a section is not
  specified, an ``unknown`` section will be automatically selected.

``weight``
  Optional. Positive or negative number that affects the placement of the
  parameter within the configuration file section. The heavier the "weight",
  the lower the parameter will be placed; negative numbers make the "weight"
  parameter lighter therefore it will be placed higher. If weight is not
  specified, it's set at ``0``.

Examples
~~~~~~~~

Add custom parameters:

.. code-block:: yaml

   libvirtd_qemu__configuration:

     - name: 'custom_param'
       value: 'custom-value'

Change the section and order of existing parameters:

.. code-block:: yaml

   libvirtd_qemu__configuration:

     - name: 'listen_tls'
       section: 'authn'
       weight: 30

Comment out a specific parameter conditionally:

.. code-block:: yaml

   libvirtd_qemu__configuration:

     - name: 'listen_addr'
       value: '0.0.0.0'
       state: '{{ "present"
                  if ansible_distribution == "Debian"
                  else "comment" }}'


.. _libvirtd_qemu__ref_configuration_sections:

libvirtd_qemu__configuration_sections
-------------------------------------

This list defines the sections of the :file:`/etc/libvirt/qemu.conf`
configuration file, as well as their order in the generated file. Each element
of the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the section, specified in the configuration entries as the
  ``section`` parameter. Should be short and recognizable.

``title``
  Required. A short description of the given configuration file section which
  will be added as a header.

``comment``
  Optional. a string or a YAML dictionary with additional comments about
  a given section, added after the title.

``state``
  Optional. If not specified or ``present``, the section will be included in
  the configuration file. If ``absent``, the entire section (including the
  parameters that belong to it) will be omitted in the generated configuration
  file. If ``hidden``, the section will be present but the title and section
  comment will not be included.

Examples
~~~~~~~~

Set a custom list of sections:

.. code-block:: yaml

   libvirtd_qemu__configuration_sections:

     - name: 'section-one'
       title: 'First section'

     - name: 'section-two'
       title: 'Section with hidden title'
       state: 'hidden'

     - name: 'section-three'
       title: 'Third section'
