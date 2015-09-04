Changelog
=========

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

