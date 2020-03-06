.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.sudo`` role can be used to ensure that :command:`sudo` is
supported on a host. The role will automatically install ``sudo-ldap`` APT
package if LDAP support is detected on a host, otherwise a normal ``sudo`` APT
package will be installed.
