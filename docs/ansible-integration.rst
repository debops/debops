Ansible integration and role design
===================================

.. include:: includes/all.rst

Design goals
------------

* :command:`firecfg` is not being used to enabling/disabling
  :ref:`system wide sandboxes <firejail__ref_system_wide_sandboxed>`.
  This is done by the role itself to have more control over the process.

  Note that running :command:`firecfg` without arguments will have a similar
  affect than when using this role with
  :envvar:`firejail__global_profiles_system_wide_sandboxed` set to
  `if_installed <firejail__ref_system_wide_sandboxed_if_installed>`_ but
  without all the other logic of this role.
  So :command:`firecfg` might change settings done by the role. You can rerun
  the role to ensure that the state defined by Ansible is present on the
  system.

Alternative roles
-----------------

As of 2016-10-31 ypid_ was aware of two alternative Ansible roles for Firejail:

* `gbraad.firejail <https://galaxy.ansible.com/gbraad/firejail/>`_, targets Fedora, has a major security issue: `Installation can be trivially MITMed leading to the system being comprised <https://github.com/gbraad/ansible-role-firejail/issues/2>`_. Only deals with installing the Firejail suite itself.
* `Firejail role <https://bitbucket.org/aaaaaaaaaaaaaaaaaaaaa1/ansible-firejail>`_ by `aaaaaaaaaaaaaaaaaaaaa1 <https://bitbucket.org/aaaaaaaaaaaaaaaaaaaaa1/>`_, targets system which use APT_. Only deals with building and installing Firejail itself.

None of the existing roles where found to be a suitable start for this role so
it has been designed and written from scratch.
