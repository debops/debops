.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops sftp` command runs an interactive file transfer
session with a host of the Ansible inventory. The destination follows the
grammar of :command:`sftp`: ``[user@]host[:path]``. The host name resolves
through the inventory of the active view, which supplies the address, the
user, the port, the private key and the jump hosts. The optional path is
the directory in which the session starts.

The options of DebOps are parsed in front of the destination. The options
which DebOps does not interpret are passed to :command:`sftp` unchanged,
in front of the destination or after it, in the place they were written.

.. warning::

   The ``-a`` option of :command:`debops sftp` accepts an unseen SSH host
   key on the first contact. The ``-a`` option of :command:`sftp` resumes
   interrupted transfers. To use the ``resume`` option of
   :command:`sftp`, write it after the destination:

   .. code-block:: console

      alice@controller:~$ debops sftp web-1 -a

The ``--`` marker before the destination hands the rest of the arguments
to :command:`sftp` verbatim. The inventory is not consulted and the
known_hosts store of the project is not applied.
