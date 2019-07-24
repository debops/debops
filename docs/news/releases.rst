DebOps release schedule
=======================

The DebOps project is used to manage production infrastructure which requires
a stable, predictable codebase. This document describes the various steps
involved in the DebOps development to get to a stable release. It is meant to
aid the project users in picking the preferred release schedule for their
needs.


The ``master`` branch
---------------------

DebOps project is developed in a :command:`git` repository, with the ``master``
branch as the main development branch. The project's repository is `hosted on
GitHub`__, with a `mirror on GitLab`__ used for testing the Ansible roles via
a GitLab CI pipeline.

.. __: https://github.com/debops/debops/
.. __: https://gitlab.com/debops/debops/

The changes in the ``master`` branch are performed in the form of pull requests
from forked :command:`git` repositories, usually on separate branches with one
or more :command:`git` commits. The ``master`` branch is designed to be usable
at all times in the production environment, but uncatched bugs might occur;
they are usually quickly fixed if found.

The :command:`debops.update` script included in the ``debops`` Python package
by default clones the project's :command:`git` repository to a central location
and checks out the ``master`` branch.


The versioned :command:`git` tags
---------------------------------

Starting from ``v1.1.0`` release, each significant change in the codebase is
tagged using `Semantic Versioning`__ scheme. Each part of the version (*major*,
*minor*, *patch*) has a specific meaning designed to let users quickly estimate
the amount of changes between releases. Below you can find examples of changes
that modify each part of the version number.

.. __: https://semver.org/

Patch releases
~~~~~~~~~~~~~~

- Changes in the Ansible roles or playbooks that do not touch the existing
  infrastructure managed by DebOps, for example `code refactoring`__, updates
  to the documentation.

  .. __: https://en.wikipedia.org/wiki/Code_refactoring

- New Ansible roles or playbooks which are not included in the
  :file:`common.yml` playbook and require explicit activation via Ansible
  inventory.

- Changes in role default variables that do not modify the default conditions
  in a significant way, for example addition or removal of software packages to
  install on a host.

Minor releases
~~~~~~~~~~~~~~

- New Ansible roles or playbooks included in the :file:`common.yml` playbook.

- Changes to role dependencies in Ansible playbooks (soft dependencies) or in
  the :file:`meta/main.yml` file of a role (hard dependencies).

- Removal or existing Ansible roles of playbooks.

- Modifications in Ansible roles that require manual intervention in the
  managed infrastructure; changes needed are described in the
  :ref:`upgrade_notes` documentation. Some modifications might require
  a rebuild of a part of the infrastructure, for example a LDAP database with
  incompatible schema changes.

- Changes to role default variables that require modification of the Ansible
  inventory, for example variable renames, changed value types.

- Changes in external resources - new software versions, operating system
  releases, updated GPG keys.

Major releases
~~~~~~~~~~~~~~

- Major releases are considered "epochs", they happen when a significant
  portion of the project has changed sufficiently that a rebuild of the entire
  environments might be needed. The major release can also happen periodically,
  when sufficient number of minor releases was created.

New *minor* release resets the *patch* release to ``0``. New *major* release
resets the *minor* and *patch* releases to ``0.0``.

Tagged DebOps releases are published to the `Python Package Index`__ (the
``debops`` Python package includes the Ansible roles and playbooks), and to the
`Ansible Galaxy`__ as an exported Ansible Collection. The releases are also
`tagged on GitHub`__, however non-LTS tarballs are not signed.

.. __: https://pypi.org/project/debops/
.. __: https://galaxy.ansible.com/debops/debops
.. __: https://github.com/debops/debops/releases


Long Term Support (LTS) releases
--------------------------------

Around every three months, a new stable (LTS) release is created from the
current ``master`` branch. Stable DebOps releases have their own ``stable-x.y``
branches and are supported for about a year after their first release. Each new
LTS release is at least a *minor* release, which resets its *patch* release
number to ``0``.

Only bugfixes and non-invasive changes are backported from the ``master``
branch to a ``stable-x.y`` branch during its lifetime, as long as they are
compatible. Changes in external resources (for example new operating system
releases) might also be backported to the stable releases to ensure correct
operation of the roles.

The ``stable-x.y`` DebOps releases are published on GitHub with signed
tarballs, as well as in Python Package Index and Ansible Galaxy. A good
solution for multiple environments with different stable DebOps releases is to
add the DebOps monorepo as a `git submodule`__ in the project repository
:file:`debops/` subdirectory. The included scripts will prefer this repository
over the centrally deployed one. Pinning either a specific :command:`git` tag,
or the ``stable-x.y`` branch should be possible.

.. __: https://git-scm.com/book/en/v2/Git-Tools-Submodules

At the moment there are no plans to ensure that an automatic migration from one
stable release to the next is possible. This might change in the future, when
all of the old code is cleaned up and refactored. Changes between stable
releases are described in the :ref:`changelog` and the :ref:`upgrade_notes`.


Current stable releases
-----------------------

- Latest release: ``stable-1.0`` (`GitHub`__, `differences from master`__,
  `Changelog`__)

.. __: https://github.com/debops/debops/tree/stable-1.0
.. __: https://github.com/debops/debops/compare/stable-1.0
.. __: https://docs.debops.org/en/stable-1.0/news/changelog.html

=============== ============ =============== ================
 Branch/Tag      Status       First release   End of support
--------------- ------------ --------------- ----------------
``stable-1.x``  Planned      2020-02-xx      2021-02-xx
--------------- ------------ --------------- ----------------
``stable-1.x``  Planned      2019-11-xx      2020-11-xx
--------------- ------------ --------------- ----------------
``stable-1.x``  Planned      2019-08-xx      2020-08-xx
--------------- ------------ --------------- ----------------
``stable-1.0``  Supported    2019-05-22      2020-05-22
--------------- ------------ --------------- ----------------
``v0.8.1``      Retired      2019-02-02
--------------- ------------ --------------- ----------------
``v0.8.0``      Retired      2018-08-06
--------------- ------------ --------------- ----------------
``v0.7.1``      Retired      2018-03-28
--------------- ------------ --------------- ----------------
``v0.7.0``      Retired      2018-02-11
--------------- ------------ --------------- ----------------
``v0.6.0``      Retired      2017-10-21
=============== ============ =============== ================
