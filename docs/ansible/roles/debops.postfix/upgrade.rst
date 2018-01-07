Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the Changelog for
more details about what has changed.


From debops.postfix v0.1.3 to debops.postfix v0.2.0
---------------------------------------------------

- All of the default and inventory variable names have been changed from
  ``postfix_*`` to ``postfix__*``. Furthermore, most of the old variables have
  been dropped and role uses new configuration format. There's no automated
  upgrade path planned from the old deployment to a new one.

- You should copy the existing :file:`/etc/postfix/main.cf` and
  :file:`/etc/postfix/master.cf` configuration files to a separate directory
  before executing the new role on an existing infrastructure. The files are
  overwritten automatically and information about current configuration might
  be lost.

- It should be relatively easy to define your desired Postfix configuration
  using inventory variables. The new ``debops.postfix`` role intentionally does
  not provide facilities to manage files; this is supposed to be done either in
  the other Ansible roles that use ``debops.postfix`` as a dependency, or
  alternatively can be done by the :ref:`debops.resources` Ansible role.

- Most of the functionality of the old role has been removed. It will be
  brought back using separate roles in the future, however they are not yet
  written. If you are using the old role in production, change the DebOps
  :file:`requirements.yml` configuration to pin the old role version
  (``v0.1.3``). Other roles that depend on ``debops.postfix`` will re updated
  as well, you might want to consider pinning them too.
