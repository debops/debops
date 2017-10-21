.. _ferm__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.ferm**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.ferm master`_ - unreleased
----------------------------------

.. _debops.ferm master: https://github.com/debops/ansible-ferm/compare/v0.3.0...master


`debops.ferm v0.3.0`_ - 2017-07-12
----------------------------------

.. _debops.ferm v0.3.0: https://github.com/debops/ansible-ferm/compare/v0.2.2...v0.3.0

Added
~~~~~

- Add a variable which can be used to restrict what network interfaces can be
  used for connections from Ansible Controller. [gaudenz]

- Update the Ansible facts automatically if they have been changed. [drybjed_]

Changed
~~~~~~~

- Reject other protocols besides TCP and UDP on IPv6 networks at the end of the
  chain. [gaudenz]

- Packets blocked due to rate limits will be now dropped instead of being
  rejected by default. [gaudenz]

- The data format of the firewall rules has been redesigned. Rules can now be
  defined as nested YAML lists, existing default or dependent rules can
  be easily modified through the Ansible inventory, multiple firewall rules can
  be included in one configuration file. [drybjed_]

- The firewall rules are now read from the :file:`/etc/ferm/rules.d/` directory
  to help with transition to the new data format and avoid tab-completion
  collision with the :file:`/etc/ferm/ferm.conf` file. [drybjed_]

- Use of multiple rule parameters that define the final filename of the
  configuration files has been dropped, now only the ``item.name`` parameter is
  used to define the filename. [drybjed_]

- The role automatically removes duplicate configuration files (based on the
  ``name`` parameter) when the weight of a given rule is changed to make
  modifications easier. [drybjed_]

- The scale of the "weight" used to sort the rules in the directory has been
  changed from 00-99 to 000-999. [drybjed_]

- The ``item.weight`` parameter is now relative to the "weight class" or rule
  type defined for a given firewall rule. You can use negative weight values
  for better control over rule order. [drybjed_]

- Run the ``debconf`` task only when APT is the package manager. This should
  allow the role to be used on OSes other than Debian/Ubuntu. [drybjed_]

- The :file:`/etc/ferm/ferm.conf` configuration file will be now properly
  diverted to preserve the original. [drybjed_]

Removed
~~~~~~~

- The ``ferm__default_weight`` variable has been removed. The default rule
  weight is defined in the weight map directly. [drybjed_]

- The role will no longer create the :file:`/etc/ferm/ferm.d/` directory by
  default. Existing directories are not removed. [drybjed_]

- The ``item.when`` and ``item.delete`` parameters are no longer supported. You
  can control rule presence conditionally using ``item.rule_state`` or
  ``item.state`` parameters. [drybjed_]


`debops.ferm v0.2.2`_ - 2016-12-01
----------------------------------

.. _debops.ferm v0.2.2: https://github.com/debops/ansible-ferm/compare/v0.2.1...v0.2.2

Added
~~~~~

- Write missing role documentation. [ganto_, ypid_, drybjed_]

- Allow to disable ``ferm__rules_forward`` using
  :envvar:`ferm__forward_accept`. [ypid_]

Changed
~~~~~~~

- Use the `Ansible package module`_ which requires Ansible v2.0. [ypid_]

- Be more precise about the expected format of ``item.by_role`` in
  :ref:`ferm__ref_default_rules`. [ypid_]

- Move kernel parameters to enable reverse path filtering to the
  debops.sysctl_ role. [ypid_]

Fixed
~~~~~

- Don’t create duplicate forward rules when an interface has both an IPv4 and
  an IPv6 address. [ypid_]

- Allow DHCPv6 responses for clients. [ypid_]

Deprecated
~~~~~~~~~~

- Use ``item.rule_state`` in the role defaults instead of the hereby deprecated
  ``item.when`` and ``item.delete``.
  See `discussion <https://github.com/debops/ansible-apt_preferences/issues/12>`_.
  ``item.delete`` and ``item.when`` are currently still supported for backwards
  compatibility. [ypid_]

- Deprecated ``item.role``, use ``item.by_role`` instead. Applies for:
  :ref:`ferm__ref_default_rules`. [ypid_]


`debops.ferm v0.2.1`_ - 2016-04-21
----------------------------------

.. _debops.ferm v0.2.1: https://github.com/debops/ansible-ferm/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Rename ``item.state`` parameter to ``item.rule_state`` to avoid collision
  with ``iptables state`` module support. [drybjed_]


`debops.ferm v0.2.0`_ - 2016-04-20
----------------------------------

.. _debops.ferm v0.2.0: https://github.com/debops/ansible-ferm/compare/v0.1.6...v0.2.0

Added
~~~~~

- Support ``item.state`` key in ``ferm_*_rules`` variables to add or remove
  firewall rules. [drybjed_]

Changed
~~~~~~~

- Rename all role variables to put them in their own namespace. [drybjed_]


`debops.ferm v0.1.6`_ - 2016-04-20
----------------------------------

.. _debops.ferm v0.1.6: https://github.com/debops/ansible-ferm/compare/v0.1.5...v0.1.6

Added
~~~~~

- Create base documentation files, clean up default variables. [ganto_, drybjed_]

Changed
~~~~~~~

- Enable the firewall if ``ansible_local`` and local Ansible facts are
  undefined. This will ensure that the role works on hosts which don't have it
  applied yet. [drybjed_]

- Renamed ``ferm_.*rules`` to ``ferm__.*rules`` and ``ferm_forward`` to :envvar:`ferm__forward`.
  Old names are currently still supported to not break stuff while updating the
  code which depends on the old names. [ypid_]

Removed
~~~~~~~

- Remove ``ferm_local_tags`` variable and its use in ``ferm_enabled``. This
  solution was needed when the POSIX capability detection was located in the
  tasks. Because now the templating is done in default variables which can be
  easily overridden by Ansible inventory, having a separate way of affecting
  POSIX capability detection is unnecessary.


`debops.ferm v0.1.5`_ - 2016-02-20
----------------------------------

.. _debops.ferm v0.1.5: https://github.com/debops/ansible-ferm/compare/v0.1.4...v0.1.5

Changed
~~~~~~~

- Restart :program:`fail2ban` when firewall rules are flushed, in case it's set up on
  the host. [bleuchtang]

- Restart :program:`ferm` only when the firewall rules have been modified, to not rest
  the firewall counters on every Ansible run. [Logan2211, drybjed_]


`debops.ferm v0.1.4`_ - 2016-02-07
----------------------------------

.. _debops.ferm v0.1.4: https://github.com/debops/ansible-ferm/compare/v0.1.3...v0.1.4

Added
~~~~~

- Add a way to copy custom files to remote hosts before starting the firewall.
  This allows users to add custom scripts that generate firewall rules in case
  of more esoteric environments. [drybjed_]

Changed
~~~~~~~

- Change the sysctl configuration from a handler to a conditional task. This
  should make sure ``debops.ferm`` works on older operating systems. [drybjed_]

- Move the logic that enables or disables :program:`ferm` to a default variable to
  consolidate it in one place. [drybjed_]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed_]

- Change the way ``debops.ferm`` disables :program:`ferm` support to avoid idempotency
  issues with ``ansible_managed`` variable. [drybjed_]

- Change what variable ``debops.ferm`` looks for when checking if :program:`ferm`
  should be enabled depending on current host capabilities. Now role will check
  the status in ``ansible_local.tags`` variable which is configured by the
  debops.core_ role. [drybjed_]

- Do not remove or generate firewall rules when :program:`ferm` is disabled to improve
  Ansible performance. [drybjed_]


`debops.ferm v0.1.3`_ - 2015-11-13
----------------------------------

.. _debops.ferm v0.1.3: https://github.com/debops/ansible-ferm/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add set of predefined :program:`ferm` variables used by other Ansible roles. [drybjed_]

Changed
~~~~~~~

- Redesign hook support. Instead of patching the :program:`ferm` init script, use
  internal ``@hook`` commands to run scripts in specific directories using
  ``run-parts``. [drybjed_]


`debops.ferm v0.1.2`_ - 2015-11-12
----------------------------------

.. _debops.ferm v0.1.2: https://github.com/debops/ansible-ferm/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add support for different "weight classes" of rules.

  This should help manage order of firewall rules. Each rule can specify its
  own weight class along with weight, the class will be checked in the
  ``ferm_weight_map`` dictionary, if a corresponding entry is found, its weight
  will be used for that rule, if not, the weight specified in the rule will be
  used instead. [drybjed_]

- Add ``hashlimit`` filter, move filtering rules.

  New ``hashlimit`` filter allows configuration of firewall rules using
  ``hashlimit`` module.

  Existing firewall rules which filtered ICMP and TCP SYN packets, defined in
  :file:`/etc/ferm/ferm.conf`, have been moved to their own configuration files in
  :file:`/etc/ferm/rules/filter/input/` directory. [drybjed_]

- Add ``accept`` filter template which can be used to create rules that match
  interfaces, ports, remote IP addresses/subnets and can accept the packets,
  reject, or redirect to a different chain. [drybjed_]

- Add a separate ``&log()`` ferm function and use it for logging packets in
  other :program:`ferm` rules. [drybjed_]

- Add ``item.interface_present`` and ``item.outerface_present`` parameters to
  ``active`` rule template. These parameters check if specified network
  interfaces exist before adding the firewall rules. [drybjed_]

Changed
~~~~~~~

- Move firewall rules into :file:`rules/` subdirectory.

  All directories in :file:`/etc/ferm/` that contain firewall rules in different
  chains have been moved to :file:`/etc/ferm/rules/` subdirectory for more
  readability.

  This is an incompatible change, check on a test host first to see what will
  happen.

  This change will recreate all rule directories and all default firewall
  rules. If you added your own rules in Ansible inventory or other roles, make
  sure that you re-run these roles to recreate their rules as well. To not
  create duplicate firewall rules, :program:`ferm` will only include rules from the
  new directories. [drybjed_]

- Rename ``conntrack`` list, rebalance rule weight.

  This change will create new ``conntrack`` rules with different filenames due
  to changed weight of the rules and addition of "weight classes". Make sure to
  remove the old rules manually to not create duplicates. [drybjed_]

- Rename :program:`ferm` variable to ``ferm_enabled``.

  This change is needed to avoid issues with Ansible templating the :program:`ferm`
  package in lists with contents of the :program:`ferm` variable.

  If you have :program:`ferm` disabled anywhere (set to ``False``), you will need to
  change the name of the variable in inventory to the new one before running
  this role. Otherwise there should be no changes necessary. [drybjed_]

- Move the default loopback accept :command:`iptables` rule to the new directory-based
  setup. [drybjed_]

- Rename the ``ferm_filter_domains`` default variable to ``ferm_domains`` to
  indicate that it is used in all firewall contexts, not just the "filter"
  table. [drybjed_]

- Redesign the directory structure of :program:`ferm` configuration.

  Different parts of the firewall configuration will be stored and managed in
  :file:`/etc/ferm/ferm.d/` directory instead of various subdirectories. This makes
  management of configuration simpler and more flexible to adapt to different
  environments.

  Existing firewall configuration in :file:`/etc/ferm/filter-input.d/` will be
  included by default, so the already configured firewalls still work. This
  will change after roles are converted to the new firewall configuration
  style. [drybjed_]

- Update configuration templates in :file:`templates/etc/ferm/ferm.d/` role
  directory. A few new templates have been added which will generate rules that
  were defined in :file:`/etc/ferm/ferm.conf` configuration files. [drybjed_]

- Split :file:`/etc/ferm/ferm.conf` config into parts.

  Static firewall configuration in :file:`/etc/ferm/ferm.conf` has been split into
  separate files in :file:`/etc/ferm/ferm.d/` directory. Each firewall rule is
  generated using templates, defined in default variables, which makes it
  easier to change or redesign the firewall from scratch.

  Some default variables have been renamed to better indicate their use in the
  firewall configuration. [drybjed_]

- Switch Ansible Controller accept rules to new configuration structure.
  [drybjed_]

- Rule definitions can now specify ``item.role_weight`` parameter which is
  added after ``item.role`` parameter. This allows to set the same
  ``item.weight`` for all rules of a particular Ansible role and still lets you
  order rules within the role itself. [drybjed_]

- Change default ``hashlimit`` rule target to ``RETURN``, this allows packets
  to be filtered further in the firewall instead of accepting them right away.
  [drybjed_]

- Change default ``recent`` rule target to ``NOP``, this ensures that if no
  other target is specified, rule will still be added to the firewall.
  [drybjed_]

- Convert forward firewall rules to the new :program:`ferm` configuration. [drybjed_]

Removed
~~~~~~~

- Remove :program:`ferm.d/chain.conf.j2` Ansible template as well as other unused
  templates. Functionality of this template is replaced by
  :program:`ferm.d/accept.conf.j2` template. [drybjed_]


`debops.ferm v0.1.1`_ - 2015-10-08
----------------------------------

.. _debops.ferm v0.1.1: https://github.com/debops/ansible-ferm/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add support for ferm init script hooks.

  :program:`ferm` supports "hooks" in its configuration which allow to run custom
  commands, however only three hooks are supported at this time:

  * "pre" - commands are executed before rules are applied,
  * "post" - commands are executed after rules are applied,
  * "flush" - commands are executed after rules are flushed.

  However for certain use cases this is not enough.

  This patch adds support for running custom scripts during different points in
  the :program:`ferm` init script:

  * "pre-start" - before :program:`ferm` service is started,
  * "post-start" - after :program:`ferm` service is started,
  * "pre-reload" - before :program:`ferm` service is reloaded,
  * "post-reload" - after :program:`ferm` service is reloaded,
  * "pre-stop" - before :program:`ferm` service is stopped,
  * "post-stop" - after :program:`ferm` service is stopped.

  This should provide sufficient methods to manipulate firewall dynamically
  outside of :program:`ferm` itself and allow to correctly preserve :command:`ip(6)tables`
  rules when :program:`ferm` is restarted or reloaded. [drybjed_]

- Add a ``ferm_default_rules`` list variable with a set of default firewall
  rules for all hosts.

  Connection tracking rules from main :program:`ferm` configuration file are moved to
  the new directory-based rule structure. They are defined in a separate list
  variable included in ``ferm_default_rules``. [drybjed_]

- Add support for specifying incoming and outgoing network interfaces in
  :file:`filter/conntrack.conf.j2` template. [drybjed_]

- Add "custom" rule template. [drybjed_]

Changed
~~~~~~~

- Switch ``debops.ferm`` from using :program:`ferm` binary directly to restarting and
  stopping :program:`ferm` system service. [drybjed_]

- Due to the huge number of subdirectories in :file:`/etc/ferm/` that need to be
  created, their creation is moved to a separate shell script, which will be
  run once at the first install of the :program:`ferm` firewall.

  Script creates new directory structure for firewall rules. [drybjed_]

- Enable support for the new, directory-based :command:`iptables` rules management
  system. New ``item.category`` and ``item.table`` rule arguments allow to
  specify the source template and destination firewall table where rules should
  be generated. Rules are defined in existing ``ferm_*_rules`` list variables.

  Old rules are still supported to enable easy transition to the new system.
  [drybjed_]

- Fix missing closing bracket. [drybjed_]

- Copy ``init-hooks.patch`` file to remote host and patch it from there to fix
  issues with ``patch`` module on older versions of Ansible. [drybjed_]

- Move tasks that patch :program:`ferm` init script to separate task list and add
  a condition that only does the patching if :program:`ferm` is enabled. [drybjed_]


debops.ferm v0.1.0 - 2015-09-04
-------------------------------

Added
~~~~~

- Add Changelog [drybjed_]

- Add rule template for simple DMZ-like redirection from public to private IPv4
  addresses. [drybjed_]

- Add ``item.name`` rule option to specify custom names in rule filenames.
  [drybjed_]

- Add support for :program:`fail2ban`. If :program:`fail2ban-server` is installed and is
  currently active, :program:`ferm` will reload :program:`fail2ban` rules after firewall
  configuration is finished. [drybjed_]

- Add a workaround Ansible emitting ``true`` and ``false`` as boolean values.
  [drybjed_]

- Add Ansible tags to tasks that manage the firewall rules to make reloading of
  them faster. [drybjed_]

Changed
~~~~~~~

- Move the :program:`ferm` package into ``ferm_packages`` list and rewrite the task to
  only use the list variable without Jinja templating. This fixes the "It is
  unnecessary to use '{{' in loops" error. [drybjed_]
