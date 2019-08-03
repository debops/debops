DebOps release schedule
=======================

The DebOps project is used to manage production infrastructure which requires
a stable, predictable codebase. This document describes the various steps
involved in the DebOps development to get to a stable release. It is meant to
aid the project users in picking the preferred release schedule for their
needs.

.. contents::
   :local:
   :depth: 2


The "rolling" release
---------------------

DebOps project is developed in a :command:`git` repository, with the ``master``
branch as the main development branch. The project's repository is `hosted on
GitHub`__, with a `mirror on GitLab`__ used for testing the Ansible roles via
a GitLab CI pipeline. This release is meant for those that prefer to get the
latest updates in the codebase, bugfixes and improvements.

.. __: https://github.com/debops/debops/
.. __: https://gitlab.com/debops/debops/

The changes in the ``master`` branch are performed in the form of pull requests
from forked :command:`git` repositories, usually on separate branches with one
or more :command:`git` commits. The ``master`` branch is designed to be usable
at all times in the production environment, but uncatched bugs might occur;
they are usually quickly fixed if found.

How to use the rolling release ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install or update the rolling release of DebOps after installing the
``debops`` Python package by executing the :command:`debops-update` script. It
will install the DebOps repository in the :file:`~/.local/share/debops/debops/`
directory and perform the :command:`git pull` command if it already exists. The
default branch is set to ``master``, but can be changed using the :command:`git
checkout` command if desired. The :command:`debops` script knows about this
central repository location and will use it, if found.

Alternatively, you can clone or symlink the DebOps repository into the
:file:`debops/` subdirectory inside of a given DebOps project directory
containing the Ansible inventory and other related files. This repository will
take precedence over the centralized repository described above. You can
maintain this repository by hand, or attach it as a :command:`git submodule` on
a branch, tag or specific commit.

If you plan to use the rolling release, keep an eye for changes in the project
described in the :ref:`changelog` and the :ref:`upgrade_notes`.


The "stable" releases
---------------------

Around every three months, a new stable, long term support (LTS) release is
created from the current ``master`` branch. Stable DebOps releases have their
own ``stable-x.y`` branches and are supported for about a year after their
first release.

Versioning scheme
~~~~~~~~~~~~~~~~~

The stable DebOps releases utilize the `Semantic Versioning`__ scheme in the
:command:`git` tags, with some changes from the standard scheme
(MAJOR.MINOR.PATCH):

.. __: https://semver.org/

- The **major** number in the version string is considered an "epoch" and is
  incremented after a significant number of stable *minor* releases has been
  created. A new "epoch" might signify that enough changes have happened that
  a complete rebuild of the environment managed by DebOps might be necessary.

- The **minor** number in the version string defines a stable DebOps release
  with its own ``stable-x.y`` branch.

  Only bugfixes and non-invasive changes, that don't require modification in
  the Ansible inventory or managed environment, are backported from the
  ``master`` branch to a ``stable-x.y`` branch during its lifetime, as long as
  they are compatible. Changes in external resources (for example new operating
  system releases) might also be backported to the stable releases to ensure
  correct operation of the roles.

  At the moment there are no plans to ensure that an automatic migration from
  one stable release to the next is possible. This might change in the future,
  when all of the old code is cleaned up and refactored. Changes between stable
  releases are described in the :ref:`changelog` and the :ref:`upgrade_notes`.

- The **patch** number in the version string denotes the next "patch" release in
  a given ``stable-x.y`` :command:`git` branch. Each *patch* release is created
  if there are any unreleased changes in a given ``stable-x.y`` branch, and no
  new changes were made for about a week. Changes in the *patch* release
  usually don't get a mention in the ``master`` branch Changelog, but get
  mentioned in the Changelog of a given ``stable-x.y`` branch.


How to use the stable releases ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stable DebOps releases are published to the `Python Package Index`__ (the
``debops`` Python package includes the Ansible roles and playbooks), and to the
`Ansible Galaxy`__ as an exported Ansible Collection. The releases are also
`tagged on GitHub`__. See the :ref:`install` documentation to learn how you can
install DebOps in various ways.

.. __: https://pypi.org/project/debops/
.. __: https://galaxy.ansible.com/debops/debops
.. __: https://github.com/debops/debops/releases


Current stable (LTS) releases
-----------------------------

- Latest release: ``stable-1.0`` (`GitHub branch`__, `differences from master`__,
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
