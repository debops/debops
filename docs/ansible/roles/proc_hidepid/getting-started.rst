.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Word of precaution
------------------

This role was written in 2018 to change ``hidepid`` for the whole system. On
2020-11-26 systemd 247 was released which introduced the ``ProtectProc``
setting. Setting ``hidepid`` for the whole system has drawbacks. Read
`Is mounting /proc with "hidepid=2" recommended with RHEL7 and later?`__ and
`Why is the mount option "hidepid=2" not used by default, is there a danger in using it?`__.

.. __: https://www.influxdata.com/blog/package-repository-for-linux/
.. __: https://security.stackexchange.com/questions/259134/why-is-the-mount-option-hidepid-2-not-used-by-default-is-there-a-danger-in-us

The way to move forward is to contribute ``ProtectProc`` to all upstream
projects, wait until Debian releases them and then potentially deprecate this
role. Until then, this role provides hardening with the potential of breaking
things.

Handling of polkit
------------------

> `Confirmed`__, giving access to /proc to polkitd user (running polkitd) is not
> enough, the authentication agent seems to requires that as well (and granting
> my user access to /proc denies the interest of hidepid).

.. __: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=860040

https://github.com/Kicksecure/security-misc/issues/173

https://github.com/systemd/systemd/issues/29893

So if polkit is detected or planned to be installed on a host, this hardening
on a system level will not be enabled.

Static GID assignment
---------------------

The ``procadmins`` group uses a static GID ``70``, chosen based on the default
set of system groups provided in Debian with usable range between 61-99. This
becomes important in environments with LXC containers where, depending on the
configuration, host and container GIDs could differ, resulting in a different
set of users being able to see the :file:`/proc` contents. Thus, the need to
synchronize the GID between distinct environments sharing the same GID
namespace (the same kernel).


Ansible local facts
-------------------

The ``debops.proc_hidepid`` role provides a set of Ansible local facts
available in the ``ansible_local.proc_hidepid.*`` hierarchy. You can use the
facts to add application UNIX accounts to the correct UNIX system group that
allows them access to the ``/proc`` filesystem.


Example inventory
-----------------

The ``debops.proc_hidepid`` role is included by default in the ``common.yml``
DebOps playbook; you don't need to add hosts to any Ansible groups to enable
it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.proc_hidepid`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/proc_hidepid.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::proc_hidepid``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
