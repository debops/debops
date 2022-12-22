.. Copyright (C) 2022 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Role development
================

This section is intended for Ansible developers of this role. If you only use
the role without modifying it, you can skip this section.

Nextcloud version upgrade
-------------------------

This is a checklist to upgrade the role to a new Nextcloud major version. It only documents steps specific to Nextcloud. DebOps procedures that are common for application version upgrades are ignored.

- Run something like :command:`git diff origin/stable23..origin/stable25 -- admin_manual/installation/nginx.rst admin_manual/installation/nginx-root.conf.sample admin_manual/installation/source_installation.rst admin_manual/installation/system_requirements.rst`
  in the `Nextcloud documentation git repo`__ and apply all changes to the role.

.. __: in https://github.com/nextcloud/documentation
