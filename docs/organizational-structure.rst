Organizational structure
========================

The Project is managed and developed by a decentralized group of people that
use it and contribute their time, skills and resources. To allow for a more
organized work, various roles are defined within the Project.

Developers
----------

This is a core team of people that contribute to the Project and direct its
evolution. They have the power to bring new Developers and Contributors into
the project. Their GPG keys are stored in
`debops-keyring <https://github.com/debops/debops-keyring>`_
which can be used for auditing.

Being a DebOps Developer does not imply any additional write access to
the Project. For now, giving Developers write access to a repository or
resource is done when there are good reasons to do so.

The UNIX group for DebOps Developers used on the project assets should be named
``debops-developers``.

Project Leader
--------------

The DebOps Project Leader is selected from the group of Developers. He/she has the
last word in any issues that arise withing the project and his decisions are
final. The Leader creates the version tags in the ``git`` repositories signed
by his/her GPG key. Also, the Leader is the only person with full write access
to all repositories and resources of the project.

The UNIX group for the DebOps Leader used on the project assets should be named
``debops-leader``.

Project Admins
--------------

The DebOps Project Admins manage the Project’s services such as websites and
mailing lists.

Contributors
------------

Every person who is contributing to the DebOps Project. The contributions need
to be reviewed by one of the DebOps Developers.

Authors
-------

The DebOps Project is divided into multiple repositories.

Each repository has their initial Author. They are mentioned as the first
copyright holder in the COPYRIGHT file of the role.

Maintainers
-----------

Each repository has their has a Maintainer. Maintainers decide what a given
repository does, develop it and can accept Pull/Merge Requests as needed. They
have full write access to the repositories. All of their commits need to be
signed by their GPG key.

Only DebOps Developers can be Maintainers. If a role was created by a Author
who is not a DebOps Developer yet, a DebOps Developer needs to be the
Maintainer.

A repository can have a team of Maintainers, in this case only one signature is
required for a commit.

Bots
----

Some functions are performed by software bots in an automated way. The bots
should use their own GPG keys, stored in
`debops-keyring <https://github.com/debops/debops-keyring>`_
for auditing.
The bots are not expected to introduce new unauthenticated code or
documentation in different repositories which is enforced by only giving the
bots access to the repositories they are working with and checking that no
commits are created by bots in unexpected repositories using the DebOps tools.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
