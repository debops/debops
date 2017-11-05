DebOps API reference v0
=======================

.. contents::
   :local:

API base URL: https://api.debops.org/v0

HTTP GET queries
----------------

/version
~~~~~~~~

Returns the current version (including minor version and patch version) of the
DebOps API as raw string.

Example: https://api.debops.org/v0/version

/license
~~~~~~~~

Returns license information about the API.

Example: https://api.debops.org/v0/license

/role/<role_owner>.<role_name>.json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the metadata for the given Ansible role.

Example: https://api.debops.org/v0/role/debops.unattended_upgrades.json

/roles/<role_owner>.json
~~~~~~~~~~~~~~~~~~~~~~~~

Returns the metadata for all Ansible role of the given role owner.

Example: https://api.debops.org/v0/roles/debops.json

/roles/<role_owner>.list
~~~~~~~~~~~~~~~~~~~~~~~~

Returns a simple list for all Ansible roles of the given role owner.

Example: https://api.debops.org/v0/roles/debops.list

/roles/count[:<owner>]
~~~~~~~~~~~~~~~~~~~~~~

Returns the total number of roles in the given name space.
The ``[:<owner>]`` is optional and allows to limit the count to the given role
owner.

Examples:

* https://api.debops.org/v0/roles/count
* https://api.debops.org/v0/roles/count:debops

Role metadata JSON format
-------------------------

:regexp:`^/role/.*\.json$` API calls return a JSON object containing the keys
described below.

:regexp:`^/roles/.*\.json$` API calls return a JSON object. The outer dict maps
from the full role name to the meta data (described below).

.. note:: ``role_format_version`` below ``0.2.0`` are not fully supported by
   this API. Keys might be missing for roles below ``v0.2.0``.
   Do a version compare for ``0.2.0`` or higher or update the roles (or fixup
   the DebOps API).

``role_owner``
  Ansible Galaxy role owner.

``role_name``
  Ansible Galaxy role name.

``normalized_role_name``
  Ansible role name as used in URLs. Currently the only case where this is
  different to ``role_name`` is when ``role_name`` is :command:`ansible` (in this case
  ``normalized_role_name`` will be ``role-ansible``).

``authors``
  List of dicts, one dict for each author.

  ``name``
    Full name of the author.

  ``nick``
    Nickname of the author.

  ``maintainer``
    Boolean value specifying if author is a maintainer.
    Only available for ``role_format_version`` ``0.2.1`` or later.

``clone_url``
  Secure git URL where the repository can be cloned from.

``description``
  Description of the repository.

``role_format_version``
  To which version of the DebOps role standard does the role comply to.
  TODO: The versions are currently not documented elsewhere.

``docs_url``
  HTML URL of the rendered documentation of the repository.

``changelog_url``
  HTML URL of the rendered changelog.

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

``tags``
  List of tags of the repository, currently equivalent with Ansible Galaxy role tags.

``test_suite_url``
  HTML URL to test suite for this repository.

``ci_badge_url``
  Image URL the build badge of the continues integration system on which the
  repository is tested.

``ci_url``
  HTML URL for the test page of the continues integration system which is used
  for the repository.

``vcs_url``
  HTML URL to the VCS platform where the repository is hosted.

``version``
  Latest released version of the repository.
  Is ``0.0.0`` when no release has been made.

``vcs_commits_since_last_release``
  Number of commits since the last release.
  Is missing when no release has been made.

``vcs_last_committer_date``
  Date of last commit in VCS.
