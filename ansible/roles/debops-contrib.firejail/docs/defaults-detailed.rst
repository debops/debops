.. _firejail__ref_default_variable_details:

Default variable details
========================

.. include:: includes/all.rst

Some of ``debops-contrib.firejail`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _firejail__ref_program_sandboxes:

program_sandboxes
-----------------

The :envvar:`firejail__program_sandboxes` and similar dictionaries allow you to
configure program sandboxes using Firejail profiles (:manpage:`firejail-profile(5)`).
The dictionary key is the program name, the value is a dictionary with the
following supported keys:

.. _firejail__ref_system_wide_sandboxed:

``system_wide_sandboxed``
  Optional, string.
  Should the program be sandboxed with :command:`firejail` for all users of the
  system by creating a symlink under :jinja_code:`/usr/local/bin/{{ item.key }}`
  with the :command:`firejail` program binary file path as target.
  The directory path where the symlink is being created/removed
  (:file:`/usr/local/bin/`) can be changed via :envvar:`firejail__system_local_bin_path`.
  This option relies on the feature of :command:`firejail` to be called via a
  different file path which causes :command:`firejail` to act as a wrapper
  around the real program.

  These options are supported:

  ``present``
    The sandbox should be present system wide.

  .. _firejail__ref_system_wide_sandboxed_if_installed:

  ``if_installed``
    The sandbox should be present system wide but only if the program is
    installed (is found in ``PATH``) on role run.
    This can be used to not make it look like the program is installed (by
    creating a symlink with the name in the ``PATH``) and to avoid the case where
    a user tries to run the program and :command:`firejail` complaining with
    "Error: cannot find the program in the path".
    If the program is not found, then the system wide sandbox will be made
    ``absent``.

  ``absent``
    The sandbox should be absent system wide.

  ``ignored``
    A potentially existing file in :file:`/usr/local/bin/` is ignored.

  Defaults to :envvar:`firejail__global_profiles_system_wide_sandboxed`.
  Refer to :manpage:`firejail(1)` under "Desktop Integration" or `Firejail
  0.9.38 Release Announcement`_ under "Symlink invocation".

``profile``
  Optional, dictionary.
  Use a provided profile by copying it from the Ansible controller into the
  :envvar:`firejail__config_path` directory of the remote system using the
  `Ansible copy module`_.
  ``profile`` is basically just passed to the module. Refer to it’s
  documentation for details with the exception that the ``state`` parameter is
  handled properly. ``state`` defaults to ``present`` but can be set to
  ``absent`` which will cause the profile on the remote systems to become absent.
  Refer to :ref:`firejail__ref_program_sandboxes_providing_additional_profiles`
  for how this can be used.


Examples for sandboxing additional programs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sandbox the given programs on all hosts even if Firejail does not yet ship with
a profile for them:

.. code-block:: yaml

   firejail__program_sandboxes:
     jq: {}
     my_cool_program:
       system_wide_sandboxed: 'present'

The symlink for :program:`jq` will only be created if :program:`jq` is installed.
The symlink for :program:`my_cool_program` will be created regardless whether
it has been found in the ``PATH``.


Example to exclude a program from being sandboxed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the value of :envvar:`firejail__global_profiles_system_wide_sandboxed`,
the role might sandbox all programs which are installed and for which security
profiles are defined. Check out the following example in case you want to
exclude programs from being sandboxed system wide:

.. code-block:: yaml

   firejail__program_sandboxes:
     less:
       # Less can’t possibly have an issue with parsing untrusted input (TM).
       # I know what I am doing! Don’t sandbox it!
       system_wide_sandboxed: 'absent'


.. _firejail__ref_program_sandboxes_providing_additional_profiles:

Examples for providing additional profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy Firejail security profiles from the Ansible controller to all remote
systems:

.. code-block:: yaml

   firejail__program_sandboxes:
     smplayer:
       profile:
         src: '/home/user/.config/firejail/smplayer.profile'

         ## `content` can be used alternatively to `src` to provide the profile inlined
         ## (supports Jinja templating as usual):
         # content: |
         #   # {{ ansible_managed }}
         #   # smplayer security profile.
         #   noblacklist ${HOME}/.config/smplayer
         #   # And so on.

         ## `state` can be used to make the profile absent:
         # state: 'absent'

This will create :file:`/etc/firejail/smplayer.profile` on all remote systems.
