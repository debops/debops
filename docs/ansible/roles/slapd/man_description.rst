.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`OpenLDAP`__ is an open source `Lightweight DIrectory Access Protocol`__
server, that can be used for centralized directory services.

.. __: https://openldap.org/
.. __: https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol

The ``debops.slapd`` Ansible role can be used to install and manage OpenLDAP
server (:command:`slapd`) on Debian or Ubuntu hosts. The role supports easy
management of the on-line configuration (OLC) used to manage :command:`slapd`
instances and integrates with other DebOps roles like :ref:`debops.pki` and
:ref:`debops.dhparam` for additional functionality.
