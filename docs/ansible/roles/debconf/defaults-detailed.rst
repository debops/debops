.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.debconf`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _debconf__ref_entries:

debconf__entries
----------------

The ``debconf__*_entries`` variables contain list of :command:`debconf` database
entries which should be set by the role. The configuration is managed using the
:ref:`universal_configuration` system.

The syntax used in the role is a bit more streamlined version of the syntax used
by the `ansible.builtin.debconf`__ Ansible module. To see a list of currently
set :command:`debconf` answers for a given package, use the command:

.. code-block:: console

   debconf-show <package>

To see a list of possible questions for a given package, use the command:

.. code-block:: console

   debconf-get-selections | grep package

.. __: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/debconf_module.html

Examples
~~~~~~~~

Set multiple values for a custom :file:`application.deb` package:

.. code-block:: yaml

   debconf__entries:

     - name: 'application'
       options:

         - name: 'environment'
           vtype: 'select'
           value: 'production'

         - name: 'application/fqdn'
           value: 'example.com'

         - name: 'debug_enabled'
           vtype: 'boolean'
           value: True

Set default locale to fr_FR.UTF-8 and define which locales should be generated:

.. code-block:: yaml

   debconf__entries:

     - name: 'locales'
       options:

         - name: 'locales/default_environment_locale'
           vtype: 'select'
           value: 'fr_FR.UTF-8'

         - name: 'locales/locales_to_be_generated'
           vtype: 'multiselect'
           value: 'en_US.UTF-8 UTF-8, fr_FR.UTF-8 UTF-8'

Accept license of some Oracle products:

.. code-block:: yaml

   debconf__entries:

     - name: 'oracle-java7-installer'
       options:

         - name: 'shared/accepted-oracle-license-v1-1'
           vtype: 'select'
           value: 'true'

Define a site passprhase for Tripwire and store it in the
:file:`ansible/secret/` directory (see :ref:`debops.secret` for more details):

.. code-block:: yaml

   debconf__entries:

     - name: 'tripwire'
       options:

         - name: 'site-passphrase'
           vtype: 'password'
           value: '{{ lookup("password", secret + "/tripwire/credentials"
                                         + "/site-passphrase") }}'

Syntax
~~~~~~

Database entries are define using a list of YAML dictionaries with specific
syntax:

``name``
  Required. Name of the APT package to configure. Entries with the same ``name``
  parameter will be merged together and can affect each other in order of
  appearance.

``reconfigure``
  Optional, boolean. If specified and ``True``, the role will not try to
  reconfigure a given APT package during execution. This might be useful if a
  package is not expected to be installed on the system when the role is
  applied.

``options``
  Required. A list of YAML dictionaries which define questions and answers for a
  given package. The ``options`` lists from multiple configuration entries with
  the same ``name`` are merged together and can affect each other in order of
  appearance.

  Each option is defined as a YAML dictionary with specific parameters:

  ``name``
    The name of the question for a given answer. If the name does not contain
    the ``/`` character, the package name will be prepended to it (``question``
    becomes ``package/question``). If the question name contains the ``/``
    character, it will be used as-is. Questions from entries with the same
    ``name`` will be merged together in order of appearance and can affect each
    other.

  ``value``
    The answer for a given :command:`debconf` question.

  ``vtype``
    Optional. The type of the value for a given question. Supported types:
    ``boolean``, ``error``, ``multiselect``, ``note``, ``password``, ``seen``,
    ``select``, ``string`` (default), ``text``, ``title``.

    If the ``password`` type is selected, the role will automatically set the
    ``no_log=True`` for a given task item to avoid storing sensitive values in
    logs.

  ``unseen``
    Optional, boolean. If ``True``, the "seen" flag for a given question won't
    be set and :command:`debconf` might still ask the user for an answer during
    installation or re-configuration of the package. This might be used to pre-seed answers for different packages.


.. _debconf__ref_alternatives:

debconf__alternatives
---------------------

These YAML lists can be used to configure special symlinks (for example,
``editor``, ``x-terminal-emulator``, ``pager``) which can point to different
applications that provide similar functionality using the
``update-alternatives`` command.

Examples
~~~~~~~~

Configure Emacs to be the default system editor:

.. code-block:: yaml

   debconf__alternatives:

     - name: 'editor'
       path: '/usr/bin/emacs24'

Let the system decide automatically what editor to use as default:

.. code-block:: yaml

   debconf__alternatives:

     - name: 'editor'

Syntax
~~~~~~

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the symlink which should be configured.

``path``
  Optional. Absolute path to the application which should be symlinked. To see
  available alternatives, you can run the command:

  .. code-block:: console

     update-alternatives --display <name>

  If the ``path`` parameter is not specified, the role will configure a given
  symlink to select an application automatically.

``link``
  Optional. Absolute path to the file which should be symlinked. This is rarely
  needed.

``priority``
  Optional. Set a priority for a given application package. This is rarely
  needed.


.. _debconf__ref_commands:

debconf__commands
-----------------

The ``debconf__*_commands`` variables can be used to define shell commands or
small scripts which should be executed on the remote hosts. This can be useful
to, for example, start a :command:`systemd` service when it's not automatically
started after installation.

This is not a replacement for a fully-fledged Ansible role. The interface is
extremely limited, and you need to ensure idempotency inside of the script or
command you are executing. The :ref:`debops.debconf` role can be executed at
different points in the main playbook, which you should also take into account.

Examples
~~~~~~~~

Start a :command:`systemd` service after package installation:

.. code-block:: yaml

   debconf__commands:
     - name: 'Reload systemd and start example service'
       shell: |
         if ! systemctl is-active example.service ; then
             systemctl daemon-reload
             systemctl start example.service
         fi

Syntax
~~~~~~

Each shell command entry is defined by a YAML dictionary with specific
parameters:

``name``
  Required. A name of a given shell command displayed during Ansible execution,
  not used for anything else in the task. Multiple configuration entries with
  the same ``name`` parameter are merged together.

``script`` / ``shell`` / ``command``
  Required. String or YAML text block that contains the command or script to
  execute on the remote host. The contents will be passed to the ``shell``
  Ansible module.

``chdir``
  Optional. Specify the path to the directory on the remote host where the
  script should be executed.

``creates``
  Optional. Specify the path of the file on the remote host - if it's present,
  the ``shell`` module will not execute the script.

``removes``
  Optional. Specify the path of the file on the remote host - if it's absent,
  the ``shell`` module will not execute the script.

``executable``
  Optional. Specify the command interpreter to use. If not specified,
  ``/bin/bash`` will be used by default.

``state``
  Optional. If not specified or ``present``, the shell command will be executed
  as normal by the role. If ``absent``, the shell command will not be executed
  by the role. If ``ignore``, the configuration entry will not be evaluated by
  the role during execution. This can be used to conditionally activate and
  deactivate different shell commands on the Ansible level.

``no_log``
  Optional, boolean. If ``True``, Ansible will not display the task contents or
  record them in the log. It's useful to avoid recording sensitive data like
  passwords.
