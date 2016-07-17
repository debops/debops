API Reference
=============

.. contents::
   :local:

HTTP GET queries
----------------

/version
~~~~~~~~

Returns the current version of the DebOps API as raw string.

Example: https://api.debops.org/version

/license
~~~~~~~~

Returns license information about the API.

Example: https://api.debops.org/license

/role/<role_owner>.<role_name>.json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the metadata for the given Ansible role.

Example: https://api.debops.org/role/debops.unattended_upgrades.json

/roles/<role_owner>.json
~~~~~~~~~~~~~~~~~~~~~~~~

Returns the metadata for all Ansible role of the given role owner.

Example: https://api.debops.org/roles/debops.json

/roles/<role_owner>.list
~~~~~~~~~~~~~~~~~~~~~~~~

Returns a simple list for all Ansible roles of the given role owner.

Example: https://api.debops.org/roles/debops.list

/roles/count[:<owner>]
~~~~~~~~~~~~~~~~~~~~~~

Returns the total number of roles in the given name space.
The ``[:<owner>]`` is optional and allows to limit the count to the role owner.

Examples:

* https://api.debops.org/roles/count
* https://api.debops.org/roles/count:debops

Role metadata JSON format
-------------------------

:regexp:`^/role/.*\.json$` API calls return a JSON object containing the keys
described below.

:regexp:`^/roles/.*\.json$` API calls return a JSON object. The outer dict is a
full role name to meta data (described below) mapping.

.. note:: ``docs_format_version`` below ``0.2.0`` are not fully supported by
   this API. Keys might be missing for roles with this version.
   Do a version compare for ``0.2.0`` or higher of fixup the DebOps API.

``authors``
  List of dicts, one dict for each author.

  ``name``
    Full name of the author.

  ``nick``
    Nickname of the author.

``clone_url``
  Secure git URL where the repository can be cloned from.

``description``
  Description of the repository.

``docs_format_version``
  Version of the DebOps documentation format used for the repository.

``docs_url``
  HTML URL of the rendered documentation of the repository

``galaxy_url``
  HTML URL of the role on Ansible Galaxy.

``issue_url``
  HTML URL on the VCS platform where issues can be reported to.

``license``
  License of the repository, as SPDX license identifier.

``min_ansible_version``
  Minimum required Ansible version to run this role.

``platforms``
  Corresponds with ``galaxy_info.platforms`` from the :file:`meta/main.yml` file of Ansible roles.

``pr_url``
  HTML URL on the VCS platform where Pull/Merge requests can be submitted to.

``role_name``
  Ansible Galaxy role name.

``role_owner``
  Ansible Galaxy role owner.

``tags``
  List of tags of the repository, currently equivalent with Ansible Galaxy role tags.

``test_suite_url``
  HTML URL to test suite for this repository.

``travis_badge``
  Image URL the build badge of for Travis CI.

``travis_url``
  HTML URL for Travis CI.

``vcs_last_committer_date``
  Date of last commit in VCS.

``vcs_url``
  HTML URL to the VCS platform.

``version``
  Latest released version of the repository.
