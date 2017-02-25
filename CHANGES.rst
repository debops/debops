Changelog
=========

.. include:: includes/all.rst

**debops-contrib.kernel_module**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops-contrib.kernel_module v0.1.0 - unreleased
------------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

Changed
~~~~~~~

- Migrate role to `DebOps Contrib`_ as ``debops-contrib.kernel_module``.
  You might need to update your inventory. This oneliner might come in handy to
  do this.

  .. code-block:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/ypid_service_kernel_modules/debops_service_kernel_module/g;'

  [ypid_]

- Changed namespace from ``kernel_module_`` to ``kernel_module__``.
  ``kernel_module_[^_]`` variables are hereby deprecated and you might need to
  update your inventory. This oneliner might come in handy to do this.

  .. code-block:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(kernel_module)_([^_])/\1__\2/g;'

  [ypid_]

- Blacklist ``firewire-core`` and ``thunderbolt`` by default using the
  :envvar:`kernel_module__security_list` variable. [ypid_]

- Blacklist also ``firewire-ohci`` to allow successful unloading of
  ``firewire-core`` if the modules are already loaded. [ypid_]
