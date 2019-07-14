Stable releases
===============

DebOps project is developed in a :command:`git` repository, with the ``master``
branch as the main development branch. The project's repository is `hosted on
GitHub`__, with a `mirror on GitLab`__ used for testing the Ansible roles via
a GitLab CI pipeline.

.. __: https://github.com/debops/debops/
.. __: https://gitlab.com/debops/debops/

Use of the ``master`` branch for production environments is encouraged, since
this gives access to role bugfixes and new functionalities. However, due to
a rapid pace of development, it might not be ideal where more conservative
approach is needed. In that case, DebOps project offers stable releases using
the ``stable-x.y`` :command:`git` branches, as well as tagged releases.

The project uses `Semantic Versioning`__ for tags and stable releases. The
definition of the *major*, *minror* and *patch* version numbers used in DebOps
versions is:

- *Major* releases are considered "epochs", they happen when a significant
  portion of the project has changed sufficiently that a rebuild of the entire
  environments might be needed. The major release can also happen periodically,
  when sufficient number of minor releases was created.

- *Minor* releases are done periodically, usually every 6 months or so. Minor
  releases might include changes in the existing Ansible roles that require
  manual modification of the environments managed by DebOps, which are
  described in the :ref:`upgrade_notes` for each release.

- *Patch* releases are performed when there are commits in a given
  ``stable-x.y`` branch and no new changes have been done for some time,
  usually a week. The commits in ``stable-x.y`` branches are cherry-picked from
  the ``master`` branch and include bugfixes to existing code as long as the
  code is compatible, updates to external services (for example new Debian or
  Ubuntu release, updated GPG key ids, and the like). The changes in the patch
  release do not require changes in the environments managed by DebOps.

Stable releases are supported as long as the code from the ``master`` branch is
compatible. Old stable releases are usually retired after a year and don't
receive new updates. This should ensure at least two stable DebOps releases
that are supported at any given time; this number might change depending on the
amount of work required to maintain the support.

Any bugfixes in stable DebOps releases need to be applied through the
``master`` branch, as long as the code is compatible. If the code is no longer
compatible, bufixes might be applied directly to the ``stable-x.y`` branch as
long as it is currently supported.

.. __: https://semver.org/


Current stable releases
-----------------------

============ =============== ============ ============================================
 Branch       First release   Status       Links
------------ --------------- ------------ --------------------------------------------
stable-1.0   2019-05-22      Supported    `GitHub`__, `Differences`__, `Changelog`__
============ =============== ============ ============================================

.. __: https://github.com/debops/debops/tree/stable-1.0
.. __: https://github.com/debops/debops/compare/stable-1.0
.. __: https://docs.debops.org/en/stable-1.0/news/changelog.html
