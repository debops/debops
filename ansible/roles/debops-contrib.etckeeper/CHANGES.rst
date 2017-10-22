Changelog
=========

.. include:: includes/all.rst

**debops-contrib.etckeeper**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops-contrib.etckeeper v0.1.0 - unreleased
--------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Added support to configure the user and email used by etckeeper.
  [joh6nn, ypid_]

Changed
~~~~~~~

- Renamed ``etckeeper_gitignore`` to ``etckeeper_ignore_list``,
  ``etckeeper_gitignore_group`` to ``etckeeper_ignore_host_group_list``,
  ``etckeeper_ignore_host_list`` to ``etckeeper_gitignore_host``. [ypid_]

- Moved role default ignore list from ``etckeeper_ignore_list`` to it’s own
  ignore list ``etckeeper_ignore_role_list``. [ypid_]

- Changed namespace from ``etckeeper_`` to ``etckeeper__``.
  ``etckeeper_[^_]`` variables are hereby deprecated and you might need to
  update your inventory. This oneliner might come in handy to do this.

  .. code-block:: shell

     git ls-files | xargs sed --in-place --regexp-extended 's/etckeeper_([^_])/etckeeper__\1/g'

  [ypid_]
