Changelog
=========

.. include:: includes/all.rst

v0.1.3
------

- Add  ``dhparam__deploy_state`` to allow to specify the desired state this
  role should achieve. State ``absent`` is not fully implemented yet. [ypid]

v0.1.2
------

*Released: 2016-02-23*

- Move the list of APT packages to a default variable, install ``cron`` package
  when necessary. [drybjed]

- Fix deprecation warnings on Ansible 2.1.0. [drybjed]

- Rename all role variables from ``dhparam_*`` to ``dhparam__*`` to move them
  to their own namespace. [drybjed]

v0.1.1
------

*Released: 2015-11-24*

- Support Ansible check mode. [drybjed]

v0.1.0
------

*Released: 2015-10-22*

- Initial release. [drybjed]

- Reviewed and fixed spelling. [ypid]
