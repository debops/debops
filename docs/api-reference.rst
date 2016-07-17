API Reference
=============

.. contents::
   :local:

/version
--------

Returns the current version of the DebOps API as raw string.

Example: https://api.debops.org/version

/license
--------

Returns license information about the API.

Example: https://api.debops.org/license

role/<role_owner>.<role_name>.json
----------------------------------

Returns the metadata for the given Ansible role.

Example: https://api.debops.org/role/debops.unattended_upgrades.json

roles/<role_owner>.json
-----------------------

Returns the metadata for all Ansible role of the given role owner.

Example: https://api.debops.org/roles/debops.json

roles/<role_owner>.list
-----------------------

Returns a simple list for all Ansible role of the given role owner.

Example: https://api.debops.org/roles/debops.list

roles/count[:<owner>]
---------------------

Returns the total number of roles in the given name space.
The ``[:<owner>]`` is optional and allows to limit the count to the role owner.

Examples:

* https://api.debops.org/roles/count
* https://api.debops.org/roles/count:debops
