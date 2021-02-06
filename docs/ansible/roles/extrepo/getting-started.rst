.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Conflicts with other APT sources
--------------------------------

Some packages from third-party repositories, for example Google Chrome, may
install their own :file:`/etc/apt/sources.list.d/*.list` configuration files on
installation. This might result in a conflict, since :command:`extrepo`
:file:`.sources` files define a specific GPG key for each external APT source.
You might see an error message while running :command:`apt update`, for
example:

.. code-block:: none

   E: Conflicting values set for option Signed-By regarding source
      http://dl.google.com/linux/chrome/deb/ stable:
      /var/lib/extrepo/keys/google_chrome.asc !=
   E: The list of sources could not be read.

There's currently nothing the :ref:`debops.extrepo` role can do about this.
To fix these issues, you might need to comment out the additional APT sources
installed by the software package. Some third-party packages support this
situation and don't re-create the APT sources, others might not. YMMV.


Example inventory
-----------------

To install and configure ``extrepo`` on a given host, it should be included in
a specific Ansible inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_extrepo]
   hostname

By default the role does not enable any APT sources. Users can do that via
Ansible inventory using the :ref:`extrepo__*_sources <extrepo__ref_sources>`
variables. Other Ansible roles can also interface with the
:ref:`debops.extrepo` role through the :envvar:`extrepo__dependent_sources`
variable used on the playbook level.

The repository components enabled by :command:`extrepo` (``main``, ``contrib``,
``non-free``, etc.) are set using the ``ansible_local.apt.components`` Ansible
local fact. You can use the :ref:`debops.apt` role to :envvar:`enable non-free
components <apt__nonfree>` which might be needed for certain repositories, for
example `FastTrack repository`__ with packaged GitLab.

.. __: https://wiki.debian.org/FastTrack

To pick a specific version of a package from the APT repository, you can use
the :ref:`debops.apt_preferences` role.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.extrepo`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/extrepo.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::extrepo``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.extrepo`` Ansible role:

- Manual pages: :man:`extrepo(1p)`, :man:`sources.list(5)`

- `Annoucement about the extrepo package`__

  .. __: https://grep.be/blog/en/computer/debian/Announcing_extrepo/

- `Blog post`__ about some of the APT repositories available through
  :command:`extrepo`

  .. __: https://grep.be/blog/en/computer/debian/Software_available_through_Extrepo/

- The `extrepo-data repository`__ which contains metadata about third-party APT
  sources

  .. __: https://salsa.debian.org/extrepo-team/extrepo-data
