Changelog
=========

.. include:: includes/all.rst

**debops-contrib.apparmor**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops-contrib.apparmor v0.1.0 - unreleased
-------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Added :envvar:`apparmor__local_dependent_config` and
  :envvar:`apparmor__tunables_dependent` to use this role as dependency for other
  roles.

- Added ``delete`` and ``by_role`` options to :envvar:`apparmor__local_config_global`. [ypid_]

Changed
~~~~~~~

- Renamed ``apparmor_enable`` to :envvar:`apparmor__enabled`. [ypid_]

- Changed namespace from ``apparmor_`` to ``apparmor__``.
  ``apparmor_[^_]`` variables are hereby deprecated and you might need to
  update your inventory. This oneliner might come in handy to do this.

  .. code:: shell

     git ls-files -z | find -type f -print0 | xargs --null sed --in-place --regexp-extended 's/(apparmor)_([^_])/\1__\2/g'

  [ypid_]

- Use Ansible local fact ``ansible_cmdline`` to detect if kernel has been
  started with AppArmor enabled. [ypid_]

Fixed
~~~~~

- Fix support for Ubuntu Trusty. [ypid_]
