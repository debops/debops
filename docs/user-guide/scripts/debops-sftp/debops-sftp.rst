.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops sftp`
----------------------

Open an interactive file transfer session in the home directory of a host:

.. code-block:: console

   alice@controller:~$ debops sftp web-1

Open the session in a directory of the host, driven by a batch file:

.. code-block:: console

   alice@controller:~$ debops sftp -b batch web-1:/srv/files

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for the session. If
  not specified, the default view will be used automatically. Using this
  option overrides the automatic view detection performed by DebOps based on
  the current working directory.

``-i <key>, --identity <key>``
  Use this private key instead of the key defined in the inventory.

``--accept``
  Accept an unseen SSH host key on the first contact and store it in the
  active known_hosts store. This option is not related to the ``-a`` option
  of :command:`sftp`, which resumes an interrupted transfer; the ``resume``
  option of :command:`sftp` works when written after the destination:

  .. code-block:: console

     alice@controller:~$ debops sftp web-1 -a

``--eval``
  Do not connect; instead print the composed :command:`sftp` command to
  stdout.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<destination>``
  The destination of the session, in the ``[user@]host[:path]`` form. The
  host name resolves through the inventory of the active view; the optional
  path is the directory in which the session starts.

``<sftp_options>``
  The options which DebOps does not interpret are passed to
  :command:`sftp` unchanged, in front of the destination or after it, in the
  place they were written.

``--``
  Before the destination, the marker hands the rest of the arguments to
  :command:`sftp` verbatim: the inventory is not consulted and the
  known_hosts store of the project is not applied.
