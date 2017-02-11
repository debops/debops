Contributing guidelines
=======================

.. contents:: Sections
   :local:

Philosophy
----------

- Do one thing well
- Modularity and flexibility
- DebOps itself is just a name, it is the sum of its parts

Discussion
----------

Join us in `#debops <http://webchat.freenode.net/?channels=debops>`_ on Freenode
or post on the `debops <https://lists.debops.org/mailman/listinfo/>`_
mailing list.

Issue reporting
---------------

DebOps is officially hosted on Github at https://github.com/debops.

Scripts and documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

Checkout the `debops/debops issue tracker <https://github.com/debops/debops/issues>`_.

Playbooks and roles
~~~~~~~~~~~~~~~~~~~

Checkout the `debops/debops-playbooks issue tracker <https://github.com/debops/debops-playbooks/issues>`_.

Tests
~~~~~

Checkout the `debops/test-suite issue tracker <https://github.com/debops/test-suite>`_.

Code submissions
----------------

We accept `pull requests <https://help.github.com/articles/using-pull-requests>`_
on everything. Here's a quick work flow:

Fork it
~~~~~~~

- Fork it into your Github account
- Clone your fork onto your workstation
    - ``git clone git@github.com:YOURACCOUNT/the-repo.git``
- Add the official repo as your upstream
    - ``git remote add upstream https://github.com/debops/the-repo``

Make your contribution
~~~~~~~~~~~~~~~~~~~~~~

::

    git checkout -b somefeaturebranch
    git add <the files you modified>
    git push origin somefeaturebranch

Please try your best to make great commit messages. Have a read through
`better commits <http://web-design-weekly.com/2013/09/01/a-better-git-commit>`_
and research how to use ``git add -p``.

Submit your pull request through Github
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Select the branch on your repo, click the green PR button and submit it.

Update your fork
~~~~~~~~~~~~~~~~

You should do this before making any commits and after your PR has been accepted.

::

    git checkout master
    git fetch upstream
    git rebase upstream/master
    git push origin master

Code style
----------

Refer to the `DebOps Code Standards Policy <https://docs.debops.org/en/latest/debops-policy/docs/code-standards-policy.html>`_.

License agreement
-----------------

By contributing you agree that these contributions are your own
(or approved by your employer) and you grant a full, complete, irrevocable
copyright license to all users and developers of the project, present and
future, pursuant to the license of the project.
