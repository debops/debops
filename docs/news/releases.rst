DebOps releases
===============

The DebOps project is used to manage production infrastructure which requires
a stable, predictable codebase. This document describes the various steps
involved in the DebOps development to get to a stable release. It is meant to
aid the project users in picking the preferred release schedule for their
needs.

.. contents::
   :local:
   :depth: 2


Versioning scheme
-----------------

The stable and LTS DebOps releases utilize the `Semantic Versioning`__ scheme
in the :command:`git` tags, with some changes from the standard scheme
(MAJOR.MINOR.PATCH):

.. __: https://semver.org/

- The **major** number in the version string is considered an "epoch" and is
  incremented after a significant number of stable *minor* releases has been
  created. A new "epoch" might signify that enough changes have happened that
  a complete rebuild of the environment managed by DebOps might be necessary.

  New DebOps LTS releases increase the *major* version number and reset the
  *minor* version number to ``0``.

- The **minor** number in the version string defines a stable DebOps release
  with its own ``stable-x.y`` branch.

- The **patch** number in the version string denotes the next "patch" release
  in a given ``stable-x.y`` :command:`git` branch. Each *patch* release is
  created if there are any unreleased changes in a given ``stable-x.y`` branch,
  and no new changes were made for about a week in a normal "stable" release,
  or immediately in a "LTS" release. Changes in the *patch* release usually
  don't get a mention in the ``master`` branch Changelog, but get mentioned in
  the Changelog of a given ``stable-x.y`` branch.


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
at all times in the production environment, but uncaught bugs might occur;
they are usually quickly fixed if found.


The "stable" releases
---------------------

Once every three months, a new stable release is created from the current
``master`` branch, with the increased *minor* version number. Stable DebOps
releases have their own ``stable-x.y`` branches and are supported for about
a year after their first release.

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


The "LTS" releases
------------------

Once every two years, a new Long Term Support (LTS) release is created, with
a new *major* version number (``stable-x.0``). The LTS releases are similar to
the "stable" releases, but they are supported for 6 years instead of 1 year
after the initial release, to match the `Debian LTS schedule`__ for long term
support of a given OS release (additional year to account for the freeze time).

.. __: https://wiki.debian.org/LTS

The DebOps LTS releases will be created just before the current Debian Testing
release enters the "freeze" period, which is usually in November (subject to
change if the Testing freeze timeline changes). The next DebOps LTS release
will be created in October 2021 - it will be a ``v3.0.0`` release (the
``v2.0.0`` release will be created in January 2020 to re-align the DebOps
release schedule to the Debian Testing freeze schedule).


How to use different releases?
------------------------------

The "rolling" release
~~~~~~~~~~~~~~~~~~~~~

You can use the :ref:`debops-update <cmd_debops-update>` script after
:ref:`installing the "debops" Python package <install>` to clone the DebOps
monorepo to a central location. See its documentation for more details.

If you plan to use the rolling release, keep an eye for changes in the project
described in the :ref:`changelog` and the :ref:`upgrade_notes`.


The "stable" / "LTS" releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stable and LTS DebOps releases are published to the `Python Package Index`__
(the ``debops`` Python package includes the Ansible roles and playbooks), and
to the `Ansible Galaxy`__ as an exported Ansible Collection. The releases are
also `tagged on GitHub`__. See the :ref:`install` documentation to learn how
you can install DebOps in various ways.

.. __: https://pypi.org/project/debops/
.. __: https://galaxy.ansible.com/debops/debops
.. __: https://github.com/debops/debops/releases


Current release schedule
------------------------

- Latest "stable" release: ``stable-1.2`` (`GitHub branch`__, `differences from
  master`__, `Changelog`__)

.. __: https://github.com/debops/debops/tree/stable-1.2
.. __: https://github.com/debops/debops/compare/stable-1.2
.. __: https://docs.debops.org/en/stable-1.2/news/changelog.html

=============== ============ =============== ================
 Branch/Tag      Status       First release   End of support
--------------- ------------ --------------- ----------------
``stable-3.0``  Planned LTS  2021-10-xx      2027-10-xx
--------------- ------------ --------------- ----------------
...             ...          ...             ...
--------------- ------------ --------------- ----------------
``stable-2.3``  Planned      2020-10-xx      2021-10-xx
--------------- ------------ --------------- ----------------
``stable-2.2``  Planned      2020-07-xx      2021-07-xx
--------------- ------------ --------------- ----------------
``stable-2.1``  Planned      2020-04-xx      2021-04-xx
--------------- ------------ --------------- ----------------
``stable-2.0``  Planned      2020-01-xx      2021-01-xx
--------------- ------------ --------------- ----------------
``stable-1.2``  Supported    2019-12-01      2020-12-01
--------------- ------------ --------------- ----------------
``stable-1.1``  Supported    2019-08-25      2020-08-25
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
