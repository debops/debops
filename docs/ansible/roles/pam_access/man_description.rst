.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The `Linux Pluggable Authentication Modules`__ provide dynamic authentication
support to services on Linux hosts. The ``debops.pam_access`` role can be used
to manage one aspect of PAM - access control rules that can be used to grant or
revoke access to services based on users, groups and origins.

.. __: https://en.wikipedia.org/wiki/Linux_PAM
