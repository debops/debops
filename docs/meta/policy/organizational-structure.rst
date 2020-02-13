.. _debops_policy__organizational_structure:

Organizational Structure
========================

.. include:: ../../includes/global.rst

:Date drafted: 2016-06-19
:Date effective: 2016-09-01
:Last changed: 2016-08-26
:Version: 0.1.0
:Authors: - drybjed_
          - ypid_

.. This version may not correspond directly to the debops-policy version.

The Project is managed and developed by a decentralized group of people who
use it and contribute their time, skills and resources. To allow for a more
organized work, various roles are defined within the Project.

In the industry the term "organizational structure" might also be known as
"roles and missions" which is not used in this documentation to avoid confusion
with Ansible roles.

Refer to the `DebOps People`_ section in the debops-keyring_ documentation
where the people and their current roles are listed.


.. _debops_policy__structure_developers:

Developers
----------

This is a core team of people that contribute to the Project and direct its
evolution. They have the power to bring new Developers and Contributors into
the project. Their OpenPGP keys are stored in `debops-keyring`_ which can be used
for auditing.

Being a DebOps Developer does not imply write access to critical parts of
the Project. For now, giving Developers write access to a repository or
resource is done when there are good reasons to do so.
For example, when a DebOps Developer becomes a Maintainer of a repository.

Developers have write access to the following repositories:

* https://github.com/debops/test-suite
* https://github.com/debops/examples

The UNIX group for DebOps Developers used on the Project assets should be named
``debops-developers``.


.. _debops_policy__structure_project_leader:

Project Leader
--------------

The DebOps Project Leader is selected from the group of Developers. He/she has the
last word in any issue that arise within the Project and his decisions are
final. The Leader creates the version tags in the :command:`git` repositories signed
by his/her OpenPGP key. Also, the Leader is the only person with full write access
to all repositories and resources of the project.

The UNIX group for the DebOps Leader used on the Project assets should be named
``debops-leader``.


.. _debops_policy__structure_project_admins:

Project Admins
--------------

The DebOps Project Admins manage the Project’s services such as web servers and
mailing lists.


.. _debops_policy__structure_contributors:

Contributors
------------

Every person who is contributing to the DebOps Project. The contributions need
to be reviewed by one of the DebOps Developers.


.. _debops_policy__structure_authors:

Authors
-------

The DebOps Project is divided into multiple repositories.
Each repository has their initial Author. They are mentioned as the first
copyright holder in the COPYRIGHT file of the role.


.. _debops_policy__structure_maintainers:

Maintainers
-----------

Each repository has a Maintainer. Maintainers decide what a given
repository does, develop it and can accept Pull/Merge Requests as needed. They
have full write access to the repository.

Only DebOps Developers can be Maintainers. If a role was created by an Author
who is not a DebOps Developer yet, a DebOps Developer needs to be the
Maintainer.

A repository can have a team of Maintainers, in this case only one OpenPGP
signature is required for a commit to enter the main repository.


.. _debops_policy__structure_bots:

Bots
----

Some functions are performed by software bots in an automated way. The bots
should use their own OpenPGP keys, stored in `debops-keyring`_ for auditing.
The bots are not expected to introduce new unauthenticated code or
documentation in different repositories which is enforced by only giving the
bots access to the repositories they are working with and checking that no
commits are created by bots in unexpected repositories using the `DebOps
Tools`_ (`not yet implemented <https://github.com/debops/debops-tools/issues/164>`__).

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
