Organizational structure
========================

The Project is managed and developed by a decentralized group of people that
use it and contribute their time, skills and resources. To allow for a more
organized work, various roles are defined within the Project.

Developers
----------

This is a core team of people that contribute to the Project and direct its
evolution. They have the power to bring new Developers and Contributors into
the project. Their GPG keys are stored in the Project's Keyring repository
which can be used for auditing.

The UNIX group for DebOps Developers used on the project assets should be named
``debops-developers``.

Project Leader
--------------

The DebOps Project Leader is selected from the group of Developers. He/she has the
last word in any issues that arise withing the project and his decisions are
final. The Leader creates the version tags in the ``git`` repositories signed
by his/her GPG key.

The UNIX group for the DebOps Leader used on the project assets should be named
``debops-leader``.

Contributors
------------

Every person who is contributing to the DebOps Project. The contributions need
to be reviewed by one of the DebOps Developers.

Role Authors
------------

In context of Ansible roles, each role has its initial Author. They are
mentioned in the credits as the original creators of the role.

Role Maintainers
----------------

In context of Ansible roles, each role has a Maintainer. Maintainers decide
what a given role does, develop it and can accept Pull/Merge Requests as
needed. They have full write access to the role repositories. All of their
commits need to be signed by their GPG key.

Only DebOps Developers can be Role Maintainers. If a role was created by a Role
Author who is not a DebOps Developer yet, a DebOps Developer needs to be the
Role Maintainer.

A role can have a team of Role Maintainers, in this case only one signature is
required for a commit.

Bots
----

Some functions are performed by software bots in an automated way. The bots
should use their own GPG keys, stored in the Project's Keyring for auditing.
The bots are not expected to introduce new unauthenticated code or
documentation in different repositories which is enforced by only giving the
bots access to the repositories they are working with and checking that no
commits are created by bots in unexpected repositories using the DebOps tools.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
