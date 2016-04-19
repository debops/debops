Default variables: configuration
================================

Some of ``debops.ferm`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
      :depth: 1

   .. _ferm_input_list:

ferm_input_list
---------------

List of ferm INPUT rules that should be present or absent in the firewall rule
set. The same format is also used for ``ferm_input_group_list``,
``ferm_input_host_list`` and ``ferm_input_dependent_list``. Each rule is
defined as a YAML dict with the following keys:

``type``
  Name of template file to use, required. Format: ``<type>.conf.j2``

``dport``
  List of destination ports to manage, required.

``name``
  Optional. Custom name used in the generated rule filename

``weight``
  Optional. Helps with file sorting in rule directory

``filename``
  Optional. Custom filename instead of a generated one

``delete``
  Optional. Delete specified rule file. Possible values: ``False`` or ``True``

Depending on the choosen type, many additional variables are supported. Please
check the template files located in the ``templates/etc/ferm/filter-input.d/``
directory.
