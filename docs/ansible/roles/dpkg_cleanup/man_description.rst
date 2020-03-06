.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.dpkg_cleanup`` Ansible role is a "helper role", meant to be used
by other roles via the ``import_role`` Ansible module, or through a playbook.

The role helps prepare the host to clean up and revert certain files and
directories when a specific Debian/Ubuntu package is removed or purged from the
system. This ensures that customizations done by other Ansible roles are
correctly reverted and removed when a different role replaces a given
functionality with a different service - for example a webserver is switched
from :command:`nginx` to :command:`apache2`, an NTP server is changed, and the
like. This way roles that manage the same service don't necessarily have to
include code that takes care of removing parts of alternative services.

The role functions by adding a :command:`dpkg` ``pre-invoke`` hook to execute
a custom Bash script when a Debian package is removed or purged. The script
checks if a specific package is being removed/purged and before that happens,
it executes various commands that can:

- revert files diverted by the :manpage:`dpkg-divert(1)` command,
- remove files or directories not covered by the :manpage:`deb-prerm(5)`
  maintainer script included in the package,
- reload or restart :command:`systemd` services.

This helps bring back the system to a state where :command:`dpkg` can cleanly
remove or purge the package.
