Changelog
=========

.. include:: includes/all.rst

**debops-api**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer_ is ypid_.

debops-api - unreleased
-----------------------

Added
~~~~~

- Initial coding and design. [ypid_]

Security
~~~~~~~~

- The default ``yaml.load`` method from PyYAML which is used to read Ansigenome YAML files is unsafe.
  As a result remote code execution was possible when the DebOps API script parsed role metadata.

  Refer to the issue `Make load safe_load <https://github.com/yaml/pyyaml/issues/5>`_.
  This has been fixed by switching to ``yaml.safe_load``. [ypid_]
