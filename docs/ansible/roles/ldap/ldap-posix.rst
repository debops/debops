.. _ldap__ref_posix:

LDAP - POSIX environment integration
====================================

The LDAP directory uses a hierarchical structure to store its objects and their
attributes, this structure can be thought of as a N-dimesional object. In
contrast to this, POSIX or UNIX environments use a flat UID and GID namespace
of entities (users, groups, services, etc.) which can be thought of as
a two-dimesional surface.  There are different ways of representing
a N-dimesional objects on two-dimesional surfaces, unfortunately this cannot be
done without compromise.

.. contents::
   :local:


POSIX attributes
----------------

This is a list of the LDAP object attributes that are significant in a POSIX
environment, managed via the ``passwd`` database:

- ``uid``
- ``uidNumber``
- ``gidNumber``
- ``gecos``
- ``homeDirectory``
- ``loginShell``

And a similar list, for the ``group`` database:

- ``gid`` [#f1]_
- ``gidNumber``

These attributes are defined by the ``posixAccount``, ``posixGroup`` and
``posixGroupId`` LDAP object types. All of them are auxiliary [#f2]_, and can
be added to any LDAP objects in the directory.

Group membership should be defined by creating a ``groupOfNames`` LDAP object
with ``posixGroup`` and ``posixGroupId`` types and using the ``member``
attribute to specify the Distinguished Names of the group members.

`User Private Groups`__ can be defined by adding the ``posixAccount``,
``posixGroup`` and ``posixGroupId`` to a LDAP object, for example
``inetOrgPerson``. In this case the ``uid`` and ``gid`` attributes should
define the same name. Check the :ref:`slapd__ref_posixgroupid` documentation
for more details.

.. __: https://wiki.debian.org/UserPrivateGroups


Reserved UID/GID ranges
-----------------------

LDAP directory is commonly used in large, distributed environments as a global
account and group database. Because of the long operational lifetime of these
environments, counting in dozens of years or more, and issues with modification
of UID and GID values in large environments, good selection of the UID/GID
ranges reserved for use in the LDAP directory is a priority.

The `systemd`__ project has an excellent rundown of the UIDs and GIDs used on
typical Linux systems `in their documentation`__. You can also read the Debian
FAQ answer that `describes the default UNIX accounts and groups`__ present on a
Debian system. As an example of production UID/GID range allocation, you can
check the `UID/GID allocation page`__ in the documentation published by the
University of Cambridge Computer Laboratory.

.. __: https://www.freedesktop.org/wiki/Software/systemd/
.. __: https://systemd.io/UIDS-GIDS.html
.. __: https://www.debian.org/doc/manuals/securing-debian-howto/ch12.en.html#s-faq-os-users
.. __: https://wiki.cam.ac.uk/cl-sys-admin/UID/GID_allocation

For convenience, here's a summary of the UID/GID ranges typically used on Linux
hosts, copied from the ``systemd`` documentation page:

========================= ========================= =============== ==================================
                UID/GID   Purpose                   Defined By      Listed in
========================= ========================= =============== ==================================
                      0   ``root`` user             Linux           ``/etc/passwd`` + ``nss-systemd``
------------------------- ------------------------- --------------- ----------------------------------
                    1…4   System users              Distributions   ``/etc/passwd``
------------------------- ------------------------- --------------- ----------------------------------
                      5   ``tty`` group             ``systemd``     ``/etc/passwd``
------------------------- ------------------------- --------------- ----------------------------------
                  6…999   System users              Distributions   ``/etc/passwd``
------------------------- ------------------------- --------------- ----------------------------------
             1000…60000   Regular users             Distributions   ``/etc/passwd`` + LDAP/NIS/…
------------------------- ------------------------- --------------- ----------------------------------
            60001…61183   Unused
------------------------- ------------------------- --------------- ----------------------------------
            61184…65519   `Dynamic service users`__ ``systemd``     ``nss-systemd``
------------------------- ------------------------- --------------- ----------------------------------
            65520…65533   Unused
------------------------- ------------------------- --------------- ----------------------------------
                  65534   ``nobody`` user           Linux           ``/etc/passwd`` + ``nss-systemd``
------------------------- ------------------------- --------------- ----------------------------------
                  65535   16bit ``(uid_t) -1``      Linux
------------------------- ------------------------- --------------- ----------------------------------
           65536…524287   Unused
------------------------- ------------------------- --------------- ----------------------------------
      524288…1879048191   `Container UID ranges`__  ``systemd``     ``nss-mymachines``
------------------------- ------------------------- --------------- ----------------------------------
**1879048192…2147483647** **Unused**
------------------------- ------------------------- --------------- ----------------------------------
  2147483648…4294967294   HIC SVNT LEONES
------------------------- ------------------------- --------------- ----------------------------------
             4294967295   32bit ``(uid_t) -1``      Linux
========================= ========================= =============== ==================================

.. __: http://0pointer.net/blog/dynamic-users-with-systemd.html
.. __: https://manpages.debian.org/unstable/libnss-mymachines/nss-mymachines.8.en.html

The factors taken into account during the default UID/GID range selection for
the :ref:`debops.ldap` role are:

- Large number of UNIX accounts, both for normal users and applications,
  starting with 50 000+ entries, with UID/GID of a given account reserved for
  a lifetime. Yearly increase in the number of accounts being 1000-5000, for
  example in a typical university.

- Support for unprivileged LXC containers, which use their own separate
  subUID/subGID ranges in the same namespace as the LXC host. This implies that
  the selected UID/GID range needs to be half of maximum size supported by the
  operatimg system, or less, to allow for unprivileged UID/GID mapping on the
  LXC host.

- Support for `User Private Groups`__ defined in the LDAP directory, which
  allows easier collaboration between users. This means that each UNIX account
  requires its own private UNIX group, ideally with the same name as the
  account, and the same UID/GID number.

  .. __: https://wiki.debian.org/UserPrivateGroups

- Avoid collisions with existing UID/GID ranges used on Linux systems for local
  UNIX accounts and groups, or those reserved by common applications like
  ``systemd``. This implies that the UID/GID numbers <1100 should be off-limits
  for LDAP directory to not collide with common desktop PC installations.
  Ideally the 0-65535 UID/GID range should be avoided altogether to allow for
  a continuous UID/GID range which makes randomized allocation easier.

With these parameters in mind, the 1879048192…2147483647 UID/GID range,
highlighted in the table above, seems to be the best candidate to contain
a reserved LDAP UID/GID range.

Suggested LDAP UID/GID ranges
-----------------------------

The :ref:`debops.ldap` role defines a set of Ansible local facts that specify
the UID/GID range reserved for use in the LDAP directory. The range is somewhat
arbitrary and users are free to change it or not conform to the selected
UID/GID range in their environments, however the selected range affects other
applications configured by DebOps roles, for example:

- the range of subUIDs/subGIDs used for unprivileged containers
- the minimum and maximum UID/GID from the LDAP directory included in the
  ``passwd`` and ``group`` databases
- the range of UIDs/GIDs allocated randomly by account management applications
  that support this functionality

and so on. The Ansible roles that want to conform to the selected UID/GID
ranges can access them via Ansible local facts:

- :envvar:`ldap__uid_gid_min` -> ``ansible_local.ldap.uid_gid_min``
- :envvar:`ldap__uid_gid_max` -> ``ansible_local.ldap.uid_gid_max``

To allow for consistent UID/GID allocation in `User Private Groups`__,
a separate UID/GID range at the start of the allocated namespace has been
reserved to contain only groups. The UIDs/GIDs above this range should be used
only for personal or service accounts with correspodning private groups of the
same name and GID as the account. The group range is defined in Ansible local
facts as well:

- :envvar:`ldap__groupid_min` -> ``ansible_local.ldap.groupid_min``
- :envvar:`ldap__groupid_max` -> ``ansible_local.ldap.groupid_max``

.. __: https://wiki.debian.org/UserPrivateGroups

The selected LDAP UID/GID range (``2000000000-2099999999``) allows for 100 000
000 unique POSIX accounts. The range reserved for groups
(``2000000000-2001999999``) supports 2 000 000 unique groups. Users can
increase or decrease the group range inside of the maximum UID/GID range, but
going beyond that comes with a risk of exceeding the maximum UID/GID supported
by the operating system and Unforseen Consequences. The UID/GID ranges can be
divided further between different purposes, but that's beyond the scope of this
role.

With the selected ranges, a set of subUIDs/subGIDs (``210000000-420000000``) is
also possible, therefore this range should be safe to use inside of the LXC
containers. Note however, that the UID/GID range above ``2147483648`` is
considered risky due to issues in some of the kernel subsystems and userspace
tools that don't work well with UIDs outside of the signed 32bit range. This
puts an upper limit on the normal set of UID/GID numbers to ``2047483647`` if
you want to stay away from that region.

This unfortunately limits the ability to completely separate containers using
private subUID/subGID ranges for each of them, but since the UID/GID numbers
inside of the containers will belong to the same "entity" be it a person or
a service, the risk in the case of breach between LXC containers should be
minimized.


Collisions with local UNIX accounts/groups
------------------------------------------

The POSIX environments permit duplicate entries in the ``passwd`` and ``group``
databases, that is entries with the same user or group names, or duplicate
UID/GID numbers. However, most of the time, only the first entry found in the
database is returned. This might cause confusion and hard to debug issues in
the environment, or even security breaches if not handled properly.

The various DebOps roles that automatically manage custom UNIX groups or
accounts, for example :ref:`debops.system_groups`, will check if the LDAP
support is enabled on a given host. If it's enabled, they will automatically
prepend ``_`` character to any custom UNIX accounts or UNIX groups created by
them, which will affect the user or group names, home directory names,
:command:`sudo` rules, group membership, etc. The names of UNIX groups or
accounts present by default on Debian or Ubuntu systems (``adm``, ``staff``, or
other such cases) that are managed by these Ansible roles will not be changed.
For example, the local equivalent of the LDAP ``admins`` group will be changed
to ``_admins``. Local UNIX accounts of the administrators (``user``) will be
renamed to ``_user``, and so on.

These changes will not be performed on already configured hosts if the LDAP
support is enabled later on, to not create duplicate entries in the local user
and group databases. In these cases, administrators are advised to either apply
the desired modifications by themselves, or rebuild the hosts with LDAP support
enabled from scratch.

Other DebOps or Ansible roles can also implement similar modifications to UNIX
user or group names of the applications they manage, but that's not strictly
required. LDAP administrators and editors should take care that the user
(``uid``) and group (``gid``) names don't clash with the UNIX user and group
names of different applications installed locally, to not cause collisions.


.. rubric:: Footnotes

.. [#f1] The ``gid`` attribute is defined by the custom :ref:`posixgroupid LDAP
   schema <slapd__ref_posixgroupid>`, included in the :ref:`debops.slapd`
   Ansible role.

.. [#f2] The ``posixGroup`` class is changed from ``STRUCTURAL`` to
   ``AUXILIARY`` via the :ref:`rfc2307bis LDAP schema <slapd__ref_rfc2307bis>`,
   installed by the :ref:`debops.slapd` Ansible role.
