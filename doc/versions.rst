How will versions work?
=======================

The ``debops-update`` tool will orchestrate updating everything or specific
components for you.

Roles
`````

Each role will have a ``VERSION`` file in its repository.

Playbooks
`````````

The ``debops/debops-playbooks`` repository will have a ``galaxy/requirements.txt``
file which will contain a list of roles and versions. It will also have a
VERSION file in its repo.

Over time as the project matures we will create release specific branches in the
playbooks repository and they will lock in specific requirements files.

Scripts
```````

Scripts will also be versioned with release branches and a VERSION file as they
stabilize.

****

This strategy ensures that **a setup you have working today will work 3 months
down the line** even if there's been a hundred commits to half the roles and
playbooks you're using.
