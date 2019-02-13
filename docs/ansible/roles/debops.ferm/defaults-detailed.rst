Default variable details
========================

Some of ``debops.ferm`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _ferm__ref_rules:

ferm__rules
-----------

The ``ferm__*_rules`` variables are YAML lists which define what
firewall rules are configured on a host. The rules are combined together in the
:envvar:`ferm__combined_rules` variable which defines the order of the rule
variables and therefore how they will affect each other.

Each entry in the ``ferm__*_rules`` lists is a YAML dictionary. The entry needs
to have the ``name`` parameter that specifies the rule name, otherwise it will
be skipped.

The result is stored as :envvar:`ferm__parsed_rules` variable. This order
allows modification of the default rules as well as rules defined by other
Ansible roles using Ansible inventory variables.

The rules are stored in the :file:`/etc/ferm/rules.d/` directory and
the filename format is:

.. code-block:: none

   /etc/ferm/rules.d/<weight>_rule_<name>.conf

The rule "weight" is determined by a given rule type which can be overridden if
needed, see the ``type``, ``weight`` and ``weight_class`` parameters for more
details.

Each rule defined in a dictionary uses specific parameters. The parameters
described here are general ones, mostly usable on the main "level" and are
related to management of rule files. The parameters related to specific
:command:`ferm` rules are described in :ref:`ferm__ref_firewall_rules`
documentation.

``name``
  Name of the firewall rule to configure. An example rule definition:

  .. code-block:: yaml

     ferm__rules:
       - name: 'accept_all_connections'
         type: 'accept'
         accept_any: True

``rules``
  Either a string or a YAML text block that contains raw :command:`ferm`
  configuration options, or a list of YAML dictionaries which specify firewall
  rules. If this parameter is not specified, role will try and generate rules
  automatically based on other parameters specified on the "first level" of
  a given rule definition. Most of the other parameters can be specified on the
  "second level" rules and will apply to a given rule in the list.

  Example custom rule definition that restarts :command:`nginx` after firewall
  is modified:

  .. code-block:: yaml

     ferm__rules:
       - name: 'restart_nginx':
         type: 'post-hook'
         rules: '@hook post "type nginx > /dev/null && systemctl restart nginx || true";'

  Example list of rule definitions which will open access to different service
  ports; rules will be present in the same file:

  .. code-block:: yaml

     ferm__rules:
       - name: 'allow_http_https'
         rules:

           - dport: 'http'
             accept_any: True

           - dport: 'https'
             accept_any: True

``rule_state``
  Optional. Specify the state of the firewall rule file, or one of the
  rules included in that file. Supported states:

  - ``present``: default. The rule file will be created if it doesn't exist,
    a rule will be present in the file.

  - ``absent``: The rule file will be removed, a rule in the file will not be
    generated.

  - ``ignore``: the role will not change the current state of the configuration
    file. This value does not have an effect on the rules inside the file.

``comment``
  Optional. Add a comment in the rule configuration file, either as a string or
  as a YAML text block.

``template``
  Optional. Name of the template to use to generate the firewall rule file.
  Currently only one template is available, ``rule`` so this option is not
  useful yet.

``type``
  Optional. Specify the rule type as a name, for example ``accept`` or
  ``reject``. Different rule types can use different rule parameters, the rule
  type also affects the "weight" used to order the configuration files. Weight
  of the different rules is specified in the :envvar:`ferm__default_weight_map`
  variable and can be overridden using the :envvar:`ferm__weight_map` variable.

  List of known rule types can be found in the :ref:`ferm__ref_firewall_rules`
  documentation.

``weight_class``
  Optional. Override the rule type with another type, to change the sort order
  of the configuration files. This parameter does not affect the
  :command:`ferm` configuration template, only the resulting filename.

``weight``
  Optional. Additional positive or negative number (for example ``2`` or
  ``-2``) which will be added to the rule weight affecting the file sorting
  order.


.. _ferm__ref_input_list:

ferm_input_list
---------------

This is a set of legacy ``debops.ferm`` variables, kept to allow older roles to
be usable with new variables. You should use the ``ferm__*_rules`` variables
instead in new configuration, the legacy variables will be removed at some
point.

List of ferm INPUT rules that should be present or absent in the firewall rule
set. The same format is also used for :envvar:`ferm_input_group_list`,
:envvar:`ferm_input_host_list` and :envvar:`ferm_input_dependent_list`. Each rule is
defined as a YAML dict with the following keys:

``type``
  Name of template file to use, required. Format: :file:`<type>.conf.j2`

``dport``
  List of destination ports to manage, required.

``name``
  Optional. Custom name used in the generated rule filename

``weight``
  Optional. Helps with file sorting in rule directory

``filename``
  Optional. Custom filename instead of a generated one

``rule_state``
  Optional. State of the rule. Defaults to ``present``. Possible values:
  ``present`` or ``absent``

Depending on the chosen type, many additional variables are supported. Please
check the template files located in the :file:`templates/etc/ferm/ferm.d`
directory.
