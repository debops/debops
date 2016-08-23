Changelog
=========

v0.2.2
------

*Unreleased*

- Use ``item.rule_state`` in the role defaults instead of the hereby deprecated
  ``item.when`` and ``item.delete``.
  See `discussion <https://github.com/debops/ansible-apt_preferences/issues/12>`_.
  ``item.delete`` and ``item.when`` are currently still supported for backwards
  compatibility. [ypid]

Fixed
~~~~~

- Don’t create duplicate forward rules when an interface has both an IPv4 and
  an IPv6 address. [ypid]

v0.2.1
------

*Released: 2016-04-21*

- Rename ``item.state`` parameter to ``item.rule_state`` to avoid collision
  with ``iptables state`` module support. [drybjed]

v0.2.0
------

*Released: 2016-04-20*

- Support ``item.state`` key in ``ferm_*_rules`` variables to add or remove
  firewall rules. [drybjed]

- Rename all role variables to put them in their own namespace. [drybjed]

v0.1.6
------

*Released: 2016-04-20*

- Remove ``ferm_local_tags`` variable and its use in ``ferm_enabled``. This
  solution was needed when the POSIX capability detection was located in the
  tasks. Because now the templating is done in default variables which can be
  easily overridden by Ansible inventory, having a separate way of affecting
  POSIX capability detection is unnecessary.

- Enable the firewall if ``ansible_local`` and local Ansible facts are
  undefined. This will ensure that the role works on hosts which don't have it
  applied yet. [drybjed]

- Renamed ``ferm_.*rules`` to ``ferm__.*rules`` and ``ferm_forward`` to ``ferm__forward``.
  Old names are currently still supported to not break stuff while updating the
  code which depends on the old names. [ypid]

- Create base documentation files, clean up default variables. [ganto, drybjed]

v0.1.5
------

*Released: 2016-02-20*

- Restart :program:`fail2ban` when firewall rules are flushed, in case it's set up on
  the host. [bleuchtang]

- Restart :program:`ferm` only when the firewall rules have been modified, to not rest
  the firewall counters on every Ansible run. [Logan2211, drybjed]

v0.1.4
------

*Released: 2016-02-07*

- Add a way to copy custom files to remote hosts before starting the firewall.
  This allows users to add custom scripts that generate firewall rules in case
  of more esoteric environments. [drybjed]

- Change the sysctl configuration from a handler to a conditional task. This
  should make sure ``debops.ferm`` works on older operating systems. [drybjed]

- Move the logic that enables or disables :program:`ferm` to a default variable to
  consolidate it in one place. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Change the way ``debops.ferm`` disables :program:`ferm` support to avoid idempotency
  issues with ``ansible_managed`` variable. [drybjed]

- Change what variable ``debops.ferm`` looks for when checking if :program:`ferm`
  should be enabled depending on current host capabilities. Now role will check
  the status in ``ansible_local.tags`` variable which is configured by the
  ``debops.core`` role. [drybjed]

- Do not remove or generate firewall rules when :program:`ferm` is disabled to improve
  Ansible performance. [drybjed]

v0.1.3
------

*Released: 2015-11-13*

- Redesign hook support. Instead of patching the :program:`ferm` init script, use
  internal ``@hook`` commands to run scripts in specific directories using
  ``run-parts``. [drybjed]

- Add set of predefined :program:`ferm` variables used by other Ansible roles. [drybjed]

v0.1.2
------

*Released: 2015-11-12*

- Add support for different "weight classes" of rules.

  This should help manage order of firewall rules. Each rule can specify its
  own weight class along with weight, the class will be checked in the
  ``ferm_weight_map`` dictionary, if a corresponding entry is found, its weight
  will be used for that rule, if not, the weight specified in the rule will be
  used instead. [drybjed]

- Move firewall rules into ``rules/`` subdirectory.

  All directories in :file:`/etc/ferm/` that contain firewall rules in different
  chains have been moved to :file:`/etc/ferm/rules/` subdirectory for more
  readability.

  This is an incompatible change, check on a test host first to see what will
  happen.

  This change will recreate all rule directories and all default firewall
  rules. If you added your own rules in Ansible inventory or other roles, make
  sure that you re-run these roles to recreate their rules as well. To not
  create duplicate firewall rules, :program:`ferm` will only include rules from the
  new directories. [drybjed]

- Add ``hashlimit`` filter, move filtering rules.

  New ``hashlimit`` filter allows configuration of firewall rules using
  ``hashlimit`` module.

  Existing firewall rules which filtered ICMP and TCP SYN packets, defined in
  :file:`/etc/ferm/ferm.conf`, have been moved to their own configuration files in
  :file:`/etc/ferm/rules/filter/input/` directory. [drybjed]

- Rename ``conntrack`` list, rebalance rule weight.

  This change will create new ``conntrack`` rules with different filenames due
  to changed weight of the rules and addition of "weight classes". Make sure to
  remove the old rules manually to not create duplicates. [drybjed]

- Rename :program:`ferm` variable to ``ferm_enabled``.

  This change is needed to avoid issues with Ansible templating the :program:`ferm`
  package in lists with contents of the :program:`ferm` variable.

  If you have :program:`ferm` disabled anywhere (set to ``False``), you will need to
  change the name of the variable in inventory to the new one before running
  this role. Otherwise there should be no changes necessary. [drybjed]

- Add ``accept`` filter template which can be used to create rules that match
  interfaces, ports, remote IP addresses/subnets and can accept the packets,
  reject, or redirect to a different chain. [drybjed]

- Move the default loopback accept :command:`iptables` rule to the new directory-based
  setup. [drybjed]

- Rename the ``ferm_filter_domains`` default variable to ``ferm_domains`` to
  indicate that it is used in all firewall contexts, not just the "filter"
  table. [drybjed]

- Redesign the directory structure of :program:`ferm` configuration.

  Different parts of the firewall configuration will be stored and managed in
  :file:`/etc/ferm/ferm.d/` directory instead of various subdirectories. This makes
  management of configuration simpler and more flexible to adapt to different
  environments.

  Existing firewall configuration in :file:`/etc/ferm/filter-input.d/` will be
  included by default, so the already configured firewalls still work. This
  will change after roles are converted to the new firewall configuration
  style. [drybjed]

- Update configuration templates in ``templates/etc/ferm/ferm.d/`` role
  directory. A few new templates have been added which will generate rules that
  were defined in :file:`/etc/ferm/ferm.conf` configuration files. [drybjed]

- Split :file:`/etc/ferm/ferm.conf` config into parts.

  Static firewall configuration in :file:`/etc/ferm/ferm.conf` has been split into
  separate files in :file:`/etc/ferm/ferm.d/` directory. Each firewall rule is
  generated using templates, defined in default variables, which makes it
  easier to change or redesign the firewall from scratch.

  Some default variables have been renamed to better indicate their use in the
  firewall configuration. [drybjed]

- Switch Ansible Controller accept rules to new configuration structure.
  [drybjed]

- Rule definitions can now specify ``item.role_weight`` parameter which is
  added after ``item.role`` parameter. This allows to set the same
  ``item.weight`` for all rules of a particular Ansible role and still lets you
  order rules within the role itself. [drybjed]

- Change default ``hashlimit`` rule target to ``RETURN``, this allows packets
  to be filtered further in the firewall instead of accepting them right away.
  [drybjed]

- Change default ``recent`` rule target to ``NOP``, this ensures that if no
  other target is specified, rule will still be added to the firewall.
  [drybjed]

- Add a separate ``&log()`` ferm function and use it for logging packets in
  other :program:`ferm` rules. [drybjed]

- Remove :program:`ferm.d/chain.conf.j2` Ansible template as well as other unused
  templates. Functionality of this template is replaced by
  :program:`ferm.d/accept.conf.j2` template. [drybjed]

- Add ``item.interface_present`` and ``item.outerface_present`` parameters to
  ``active`` rule template. These parameters check if specified network
  interfaces exist before adding the firewall rules. [drybjed]

- Convert forward firewall rules to the new :program:`ferm` configuration. [drybjed]

v0.1.1
------

*Released: 2015-10-08*

- Switch ``debops.ferm`` from using :program:`ferm` binary directly to restarting and
  stopping :program:`ferm` system service. [drybjed]

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
  rules when :program:`ferm` is restarted or reloaded. [drybjed]

- Due to the huge number of subdirectories in :file:`/etc/ferm/` that need to be
  created, their creation is moved to a separate shell script, which will be
  run once at the first install of the :program:`ferm` firewall.

  Script creates new directory structure for firewall rules. [drybjed]

- Enable support for the new, directory-based :command:`iptables` rules management
  system. New ``item.category`` and ``item.table`` rule arguments allow to
  specify the source template and destination firewall table where rules should
  be generated. Rules are defined in existing ``ferm_*_rules`` list variables.

  Old rules are still supported to enable easy transition to the new system.
  [drybjed]

- Add a ``ferm_default_rules`` list variable with a set of default firewall
  rules for all hosts.

  Connection tracking rules from main :program:`ferm` configuration file are moved to
  the new directory-based rule structure. They are defined in a separate list
  variable included in ``ferm_default_rules``. [drybjed]

- Fix missing closing bracket. [drybjed]

- Add support for specifying incoming and outgoing network interfaces in
  ``filter/conntrack.conf.j2`` template. [drybjed]

- Copy ``init-hooks.patch`` file to remote host and patch it from there to fix
  issues with ``patch`` module on older versions of Ansible. [drybjed]

- Move tasks that patch :program:`ferm` init script to separate task list and add
  a condition that only does the patching if :program:`ferm` is enabled. [drybjed]

- Add "custom" rule template. [drybjed]

v0.1.0
------

*Released: 2015-09-04*

- Add Changelog [drybjed]

- Add rule template for simple DMZ-like redirection from public to private IPv4
  addresses. [drybjed]

- Add ``item.name`` rule option to specify custom names in rule filenames.
  [drybjed]

- Move the :program:`ferm` package into ``ferm_packages`` list and rewrite the task to
  only use the list variable without Jinja templating. This fixes the "It is
  unnecessary to use '{{' in loops" error. [drybjed]

- Add support for :program:`fail2ban`. If :program:`fail2ban-server` is installed and is
  currently active, :program:`ferm` will reload :program:`fail2ban` rules after firewall
  configuration is finished. [drybjed]

- Add a workaround Ansible emitting ``true`` and ``false`` as boolean values.
  [drybjed]

- Add Ansible tags to tasks that manage the firewall rules to make reloading of
  them faster. [drybjed]
