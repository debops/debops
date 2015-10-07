Changelog
=========

v0.1.1
------

*Released: 2015-10-08*

- Switch ``debops.ferm`` from using ``ferm`` binary directly to restarting and
  stopping ``ferm`` system service. [drybjed]

- Add support for ferm init script hooks.

  ``ferm`` supports "hooks" in its configuration which allow to run custom
  commands, however only three hooks are supported at this time:

  * "pre" - commands are executed before rules are applied,
  * "post" - commands are executed after rules are applied,
  * "flush" - commands are executed after rules are flushed.

  However for certain use cases this is not enough.

  This patch adds support for running custom scripts during different points in
  the ``ferm`` init script:

  * "pre-start" - before ``ferm`` service is started,
  * "post-start" - after ``ferm`` service is started,
  * "pre-reload" - before ``ferm`` service is reloaded,
  * "post-reload" - after ``ferm`` service is reloaded,
  * "pre-stop" - before ``ferm`` service is stopped,
  * "post-stop" - after ``ferm`` service is stopped.

  This should provide sufficient methods to manipulate firewall dynamically
  outside of ``ferm`` itself and allow to correctly preserve ``ip(6)tables``
  rules when ``ferm`` is restarted or reloaded. [drybjed]

- Due to the huge number of subdirectories in ``/etc/ferm/`` that need to be
  created, their creation is moved to a separate shell script, which will be
  run once at the first install of the ``ferm`` firewall.

  Script creates new directory structure for firewall rules. [drybjed]

- Enable support for the new, directory-based ``iptables`` rules management
  system. New ``item.category`` and ``item.table`` rule arguments allow to
  specify the source template and destination firewall table where rules should
  be generated. Rules are defined in existing ``ferm_*_rules`` list variables.

  Old rules are still supported to enable easy transition to the new system.
  [drybjed]

- Add a ``ferm_default_rules`` list variable with a set of default firewall
  rules for all hosts.

  Connection tracking rules from main ``ferm`` configuration file are moved to
  the new directory-based rule structure. They are defined in a separate list
  variable included in ``ferm_default_rules``. [drybjed]

- Fix missing closing bracket. [drybjed]

- Add support for specifying incoming and outgoing network interfaces in
  ``filter/conntrack.conf.j2`` template. [drybjed]

- Copy ``init-hooks.patch`` file to remote host and patch it from there to fix
  issues with ``patch`` module on older versions of Ansible. [drybjed]

- Move tasks that patch ``ferm`` init script to sepate task list and add
  a condition that only does the patching if ``ferm`` is enabled. [drybjed]

- Add "custom" rule template. [drybjed]

v0.1.0
------

*Released: 2015-09-04*

- Add Changelog [drybjed]

- Add rule template for simple DMZ-like redirection from public to private IPv4
  addresses. [drybjed]

- Add ``item.name`` rule option to specify custom names in rule filenames.
  [drybjed]

- Move the ``ferm`` package into ``ferm_packages`` list and rewrite the task to
  only use the list variable without Jinja templating. This fixes the "It is
  unnecessary to use '{{' in loops" error. [drybjed]

- Add support for ``fail2ban``. If ``fail2ban-server`` is installed and is
  currently active, ``ferm`` will reload ``fail2ban`` rules after firewall
  configuration is finished. [drybjed]

- Add a workaround Ansible emitting ``true`` and ``false`` as boolean values.
  [drybjed]

- Add Ansible tags to tasks that manage the firewall rules to make reloading of
  them faster. [drybjed]

