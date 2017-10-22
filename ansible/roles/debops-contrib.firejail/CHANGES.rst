Changelog
=========

.. include:: includes/all.rst

**debops-contrib.firejail**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops-contrib.firejail v0.1.0 - unreleased
-------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Support to fix desktop files using :command:`firecfg --fix`. Please use this
  to make sure that programs are actually sandboxed! [ypid_]

Changed
~~~~~~~

- Optimized performance by only checking if programs are installed when this
  actually matters (when :ref:`item.system_wide_sandboxed <firejail__ref_system_wide_sandboxed>`
  is ``if_installed``). [ypid_]

Fixed
~~~~~

- The role did not handle :envvar:`firejail__global_profiles_system_wide_sandboxed`
  set to ``absent`` correctly and instead (was handled as it was set to
  ``present``). [ypid_]

- Note in the documentation that this role requires Jinja 2.8 or later. [ypid_]

- Don’t sandbox ``tar``, ``unrar`` and :command:`git` by default. [ypid_]
