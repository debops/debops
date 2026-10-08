.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. include:: ../includes/global.rst

.. _inventory_specification:

Inventory specification
=======================

An inventory specification is a single YAML document which describes the
contents of the Ansible :file:`inventory/` directory. The specification(s) can
be applied to a project directory during initialization, creation of a new
project view, or project refresh with the ``--template`` option. DebOps
provides a set of predefined inventory specifications for convenience and as
examples.

.. contents::
   :depth: 3

Format
------

The ``hosts`` inventory specification template creates an example inventory
structure with web and database servers.

.. literalinclude:: ../../src/debops/_data/templates/inventoryspec/hosts.yml
   :language: yaml
   :lines: 4,7-

It can be used during project directory initialization using a command:

.. code-block:: console

   $ debops project init --template hosts <project_dir>

The files are created inside the inventory directory of the selected view,
:file:`ansible/inventory/` in a "legacy" project and
:file:`ansible/views/<view>/inventory/` in a "modern" one.

The specification defines this layout:

.. code-block:: text

   inventory/
   ├── group_vars/
   │   ├── all/
   │   │   ├── locales.yml
   │   │   ├── sshd.yml
   │   │   └── tzdata.yml
   │   ├── databases/
   │   │   ├── postgresql.yml
   │   │   └── postgresql_server.yml
   │   └── webservers/
   │       └── nginx.yml
   ├── hosts
   └── host_vars/
       ├── db1/
       ├── web1/
       └── web2/

Syntax
~~~~~~

Each specification is a YAML document with specific parameters.

``version``
  The version of the specification format, optional. If not specified, version
  ``0`` is assumed. DebOps refuses a document which declares a newer version
  than it understands, rather than guessing. Each project directory can define
  the maximum version allowed to be applied using configuration option.

  Each version adds one privilege to the previous one, so you can pick the
  lowest level that does what you need:

  version ``0``
   Paths and contents are written literally, nothing is rendered.

  version ``1``
   Paths are rendered as Jinja2 templates, contents are left alone.

  version ``2``
   Paths and contents are both rendered as Jinja2 templates. File contents with
   Jinja expressions need to be escaped in the templates to pass through the
   Jinja template engine into the generated files.

  version ``3``
   Paths and contents are rendered as Jinja2 templates, and the ``pipe()`` and
   ``include()`` functions become available, but only when the ``--allow-io``
   option is given. See the `Templated file contents`_ section and the
   `Commands and includes`_ section for more details.

``files``
  YAML dictionary with dictionary keys specifying the paths to create, clear or
  remove, and the value defining the operation to perform.

  Use a YAML text block (``|``) for file contents. A plain scalar works
  too, but remember that it will not have a trailing newline. A directory
  cannot carry contents, so a path which ends in ``/`` with a non-empty
  value is an error.

  .. code-block:: yaml

     ---
     files:
       group_vars/all/nginx.yml: null      # remove this file
       host_vars/legacy-host/: null        # remove this directory and its contents
       group_vars/all/: ''                 # clear directory contents, don't remove
       group_vars/all/new.yml: |           # write this file
         ---
         application__name: 'example'

  A directory which is both cleared and given new files can be reset in one
  document. The ``null`` entries are processed before the files are written, so
  the directory is removed and then re-created by the files below it.

``keep``
  Optional YAML list of paths which this specification must not remove or
  clear. The paths are relative to the inventory directory and may contain
  wildcards. Unlike ``files``, a kept path is not created when it is missing,
  and a pattern which names a non-existent file is not an error. See the
  `Paths to keep`_ section for the matching rules.

Everything else is an error, so a typo in a key name is reported instead of
silently ignoring it. The same applies to a path which is listed twice, which
YAML would otherwise resolve by keeping only the last value.

File paths
~~~~~~~~~~

Paths are relative to the inventory directory and must stay inside it. DebOps
rejects absolute paths, ``~``, ``..`` components, and anything which escapes
the inventory directory through a symbolic link.

Changes to symbolic links in the :file:`inventory/` directory are refused.
DebOps will not write through one or remove one, not even with ``--force``.
When a directory is removed or cleared, a symbolic link anywhere inside it is
refused as well.

Environment variables in paths are expanded to allow more flexibility with file
names:

.. code-block:: yaml

   ---
   files:
      group_vars/${DEBOPS_PROJECT_VIEW}/application.yml: |
        ---
        application__name: 'example'

In this example, ``${DEBOPS_PROJECT_VIEW}`` is the current infrastructure view,
set by the :command:`debops project` commands.

In a version ``0`` document, a path is written literally.

In a version ``1``, ``2`` or ``3`` document, the path is rendered as
a Jinja2 template:

.. code-block:: yaml

   ---
   version: 1
   files:
     'host_vars/{{ hostname }}/locales.yml': |
       ---
       locales__system_lang: 'en_US.UTF-8'

Environment variable expansion still applies to a path after it is rendered.
Two different paths which render to the same file in one document are an error,
since one would silently replace the other. A rendered path is validated like
any other path, so a template cannot escape the inventory either.

Templated file contents
~~~~~~~~~~~~~~~~~~~~~~~

The file contents in a version ``2`` or ``3`` of the documents are rendered as
Jinja2 templates before they are written to the inventory.

Rendering uses the variables available to the DebOps project templates:
``hostname``, ``fqdn``, ``user`` (the invoking user), ``env`` (YAML dictionary
with the process environment), ``view``, ``default_view`` and ``project``.
These are facts about the controller, so ``hostname`` names the machine DebOps
runs on, not a remote host. To target a different host, pass it in an
environment variable such as ``${TARGET}`` and use ``{{ env.TARGET }}`` in the
template. An undefined variable is an error rather than an empty
string, so a mistyped name is reported instead of defining an empty value.

Jinja expressions in file contents can be escaped with the ``{{ "{{" }}`` and
``{{ "}}" }}`` Jinja syntax in the template to preserve them in the generated
files:

.. code-block:: yaml

   ---
   version: 2
   files:
     group_vars/all/nginx.yml: |
       ---
       # resolved by Ansible on the host
       nginx__hostname_domains: [ '{{ "{{" }} ansible_domain {{ "}}" }}' ]

To escape a part of the template, it can be enclosed in a ``{% raw %}`` and
``{% endraw %}`` block:

.. code-block:: text

   {% raw -%}
   {{ ansible_facts['hostname'] }}.web.example.org
   {% endraw -%}

Take care with ``{% raw %}`` in a comment: the renderer opens the block even
when it appears to be inside one, and everything up to ``{% endraw %}`` is
passed through unchanged.

Commands and includes
~~~~~~~~~~~~~~~~~~~~~

Version ``3`` renders like version ``2`` and also makes two functions available
while rendering. They need to be explicitly allowed in the project
configuration, or the ``--allow-io`` option needs to be specified on the
command line to explicitly enable that functionality.

``pipe(command, timeout=30)``
  Run ``command`` through the shell and return its standard output with the
  trailing newline removed. The output is data, not template: Jinja2 syntax
  in it reaches the generated file as text.

  For example, ``pipe('ssh-add -L')`` expands to the public keys in your SSH
  agent. An empty command is an error. A command which exits with a non-zero
  status is reported together with its standard error, and one which runs
  longer than ``timeout`` seconds (30 by default) is killed. A command which
  is allowed to fail can end with ``|| true``, and one whose errors are noise
  can send them to ``/dev/null``.

  .. code-block:: yaml

     ---
     version: 3
     files:
       group_vars/all/access.yml: |
         ---
         root_account__authorized_keys: {{ pipe('ssh-add -L 2>/dev/null || true').splitlines() | tojson }}

``include(path)``
  Read a file and insert its contents verbatim, without rendering them again.
  The path may be absolute, may start with ``~``, may contain environment
  variables, or may be relative to the inventory directory being written, so
  that one view can pull in a shared file. A path is an error if it names a
  directory, cannot be decoded as UTF-8, or cannot be read at all:

  .. code-block:: yaml

     ---
     version: 3
     files:
       group_vars/all/secret.yml: |
         ---
         application__token: '{{ include('~/.secrets/token') | trim }}'

  Verbatim means verbatim: a text file ends with a newline, which lands in the
  rendered contents. For a whole file inserted as contents that is what you
  want, but for a single value it leaves a trailing newline in it. Unlike
  ``pipe()``, ``include()`` does not strip it, so pipe the value through
  Jinja2's ``trim`` filter, as above.

  The value is inserted into the rendered YAML as it is, so a value which
  can contain ``#``, ``:``, or a leading ``-`` or ``*`` should be quoted in
  the template or passed through ``| tojson``.

.. warning::

   The ``pipe()`` function runs an arbitrary shell command, so a version
   3 specification is only as trustworthy as the file you point ``--template``
   at.

   The ``include()`` function reads any file the invoking user can read, which
   can copy private keys or password files into the :file:`group_vars/` or
   :file:`host_vars/` in plain text. Apply a version 3 document only when you
   trust it, and remember that the keys and other data it copies are a snapshot
   taken when the command runs, not a live view.

Paths to keep
~~~~~~~~~~~~~

The ``keep`` parameter lists the paths a specification must not remove or
modify. It's used in the ``clear`` template.

.. literalinclude:: ../../src/debops/_data/templates/inventoryspec/clear.yml
   :language: yaml
   :lines: 4,7-

Apply the template with the ``--force`` option. Every file below the
:file:`group_vars/` and the :file:`host_vars/` directories will be removed
except the :file:`group_vars/all/keyring.yml` file.

How the ``keep`` list is processed:

- The ``*`` wildcard stands for any number of characters, ``?`` for exactly
  one, ``[chars]`` for one of the characters listed inside the brackets and
  ``[!chars]`` for any character which is not listed. A pattern is matched
  against the whole path relative to the inventory directory, not against one
  directory at a time.

  Since ``*`` stands for any characters, it stands for ``/`` too: the pattern
  ``*.yml`` matches :file:`group_vars/all/keyring.yml` at any depth. This
  errs towards keeping more paths than you may have expected, never fewer.
  Write the directory out, as in ``group_vars/all/*.yml``, when a pattern
  should match inside one directory only.

- The comparison is done on the string, not on the filesystem, so the result
  does not depend on how the filesystem treats case.

- The ``group_vars/all`` string keeps :file:`group_vars/all/keyring.yml` and
  every other file in that directory. The directories above a kept path are
  kept as well.

- Nothing is checked against the filesystem. A pattern for a file you have not
  created yet is fine, and a glob which matches nothing today may match
  tomorrow.

- The ``--force`` option decides whether the specification may replace paths
  which existed before the command; ``keep`` decides whether the specification
  may touch a path at all. A path in both is kept, not overwritten. The path is
  reported as kept, so ``-v`` shows which paths were spared.

- When more than one ``--template`` is given, the patterns are merged like the
  files: a later document cannot drop what an earlier one asked to keep. A
  document which changes a path which another one keeps is refused, whether it
  writes the file or removes it, because the two say opposite things about the
  same path. This also applies to a glob: if one document keeps
  ``group_vars/*.yml``, no other document may touch a file below
  :file:`group_vars/`.

- In a version ``1``, ``2`` or ``3`` document the patterns go through Jinja2
  like the paths in ``files`` do, so ``keep: ['{{ view }}/custom.yml']`` works.
  The ``pipe()`` and ``include()`` functions are not available in a pattern,
  because keeping a path is not an operation which reads or runs anything.

- A pattern must be a non-empty string. Absolute paths, ``~`` and ``..``
  components are refused, so a pattern cannot name anything outside the
  inventory directory. Environment variables in a pattern are expanded
  like the paths in ``files``.

Existing files
--------------

DebOps remembers which inventory paths existed before the command started. A
path from that set is skipped unless you pass ``--force``; a path which DebOps
itself just generated can be replaced or removed by the specification. This
lets you replace the generated :file:`hosts` file and
:file:`group_vars/all/keyring.yml` placeholders, or clear a directory, without
silently dropping variables you have set yourself. Symbolic links have no
such exception and are always refused.

.. code-block:: shell

   # print what would happen, write nothing
   debops project refresh --dry-run --template inventory.yml ~/src/projects/myproject

   # replace or remove the paths you have edited too
   debops project refresh --force --template inventory.yml ~/src/projects/myproject

   # reset an existing inventory to its defaults
   debops project refresh --force --template clear ~/src/projects/myproject

Checking the result
-------------------

A specification can easily contain a group name which does not match any group
in the inventory, and Ansible will not complain: it simply never reads those
variables. Ansible is silent about a subtler case as well: when the same
entity exists both as a file and as a directory (for example
``group_vars/all.yml`` next to ``group_vars/all/``), only the directory is
read, with no warning. Use ``--graph`` to see what Ansible actually
resolved.

.. code-block:: shell

   debops project refresh --dry-run --graph --template inventory.yml \
                          ~/src/projects/myproject

This runs :command:`ansible-inventory --graph --vars` over the files and prints
the result. Combined with ``--dry-run`` the specification is written to a
private temporary directory instead of your project, so you can check a
document before committing to it. DebOps also warns about
:file:`group_vars/` and :file:`host_vars/` entries which match no group or
host, because :command:`ansible-inventory` itself stays silent about those.

Two other views answer different questions. ``--list`` prints the whole
inventory as JSON, like :command:`ansible-inventory --list`, which is the form
to pipe into :command:`jq`:

.. code-block:: shell

   debops project refresh --list ~/src/projects/myproject | \
                          jq '._meta.hostvars | keys'

``--host <hostname>`` prints the variables Ansible resolves for one host,
which is the quickest way to confirm that a rendered
:file:`host_vars/<hostname>/` file landed where Ansible looks for it:

.. code-block:: shell

   debops project refresh --host web1.example.org ~/src/projects/myproject

All three options work with ``--dry-run`` and are mutually exclusive, just
like the matching :command:`ansible-inventory` actions. The unused-vars
warning described above is only reported for ``--graph``, because a group
without hosts and a host without variables are both missing from the other
outputs.

Reading from standard input
---------------------------

Pass ``--template -`` to read the document from standard input, which is handy
when the inventory comes from another tool:

.. code-block:: shell

   debops project init --template - ~/src/projects/myproject <inventory.yml

Standard input can only be read once, so ``-`` may be given only once per
invocation.

Combining specifications
------------------------

``--template`` can be given more than once, and files, templates and ``-`` may
be mixed. The documents are merged into a single specification before it is
applied, so the order only decides who wins for the same path: when two
documents define the same path, the one given later wins and DebOps prints a
notice:

.. code-block:: shell

   debops project init --template local --template site.yml \
                       --allow-io ~/src/projects/myproject

This works well for a shared base inventory with per-environment variables on
top of it. Here the ``site.yml`` document overrides the files the ``local``
template defines. Give the options in the other order to let the template win.

Paths which only one document defines are not affected by the order and are all
applied in the merged specification. When one document removes or clears a
directory and another writes files inside it, both operations end up in the
merged document: the removal or clear runs first, and the files are written
afterwards. That is why ``--template clear --template hosts`` resets the
inventory and then builds the ``hosts`` layout on top of it, and why reversing
those two templates does not change the result. Within a merged specification
the execution order is always the same: removals first, then empty directories,
then files.

A notice about an overridden file is only shown at ``-v`` or higher, since
it is logged at the ``NOTICE`` level like the rest of the DebOps output.

The ``keep`` patterns are merged the same way; see the `Paths to keep`_ section
for how a document which touches a kept path is treated.

Project configuration
---------------------

A "modern" project includes a ``project.inventory_spec`` section in its
:file:`.debops/conf.d/project.yml` configuration file which controls what the
``--template`` option may do in that project:

.. code-block:: yaml

   ---
   project:
     inventory_spec:

       # Set to False to refuse inventory specifications entirely
       enabled: True

       # Newest specification version this project accepts
       version: 3

       # Set to True to allow pipe() and include() without '--allow-io'
       allow_io: False

With ``enabled: False`` any use of ``--template`` is refused, whether the
specification comes from a file, from standard input or from a template
shipped with DebOps. The generated default inventory is not a specification
and is not affected.

The ``version`` option caps the specification version: a document which
declares a higher version is refused. Since ``pipe()`` and ``include()``
exist only in version 3 documents, setting ``version: 2`` is a way to forbid
I/O in a template, with no way to grant it back from the command line.

The ``allow_io`` option pre-authorizes I/O, so that a version 3 specification
does not need the ``--allow-io`` option anymore. ``--allow-io`` on the command
line still works when ``allow_io`` is ``False``; either one grants I/O for that
invocation. Set ``version: 2`` instead when you want a hard denial.

Comparison with a single YAML inventory file
--------------------------------------------

A specification does not replace a single YAML inventory file or
hand-written group definitions; it writes the inventory directory which
DebOps and Ansible already use (see the `Ansible inventory guide`__).
The specification itself is the skeleton of the inventory rather than its
finished contents. The result is an ordinary inventory which is then edited as
needed. A later run fills in what is missing and leaves those edits alone;
``--force`` re-imposes the skeleton (see `Existing files`_). When an
organization has a largely common configuration which differs in specific
places, the specification can be applied to a new inventory and adapted
afterwards.

The same applies to :ref:`infrastructure views <project_infrastructure_views>`.
:command:`debops project mkview` creates a view with its own inventory, and
its ``--template`` option, given more than once, lays the inventory out from
a set of templates instead of copying :file:`group_vars/` and
:file:`host_vars/` contents by hand.

.. __: https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html

See also
--------

- :ref:`cmd_debops-project` for the :command:`debops project` subcommands and
  the options which apply a specification, such as ``--template``,
  ``--force`` and ``--dry-run``

- :ref:`project_directory` for the structure of the project directory which
  holds the inventory
