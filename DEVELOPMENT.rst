Contribution workflow
=====================

*This is a quick guide on contributing to the development of the DebOps project.*

How to contribute via GitHub
----------------------------

If you want to contribute to DebOps using GitHub, you can start by creating
a `fork of this repository <https://github.com/debops/debops/fork>`_ and
cloning that fork to your local machine. In your local copy of the
repository, add the `official DebOps repository <https://github.com/debops/debops>`_
as an ``upstream`` of your fork.

.. code-block:: console

   git clone git@github.com:<username>/debops ~/src/github.com/<username>/debops
   cd ~/src/github.com/<username>/debops
   git remote add upstream https://github.com/debops/debops.git

Managing your local fork
~~~~~~~~~~~~~~~~~~~~~~~~

If you already have a local fork, before starting your work, fetch and rebase
the latest changes from the ``master`` branch of the upstream repository.
If you want to work on a different branch, switch to it and do the same.

.. code-block:: console

   git checkout master
   git fetch upstream
   git rebase upstream/master
   git push origin master

During development you might notice that the upstream repository has new
commits. In that case you might want to rebase your feature branch on the
latest changes in the ``master`` branch. If you have any pending changes you
don't want to commit yet, you can save them for later using :command:`git
stash`. After a rebase, you might need to resolve any conflicts manually.

.. code-block:: console

   # Save any pending changes
   git stash

   git checkout master
   git fetch upstream
   git rebase upstream/master
   git push origin master

   git checkout new-feature
   git rebase master

   # Get back stashed changes
   git stash pop

Using git with style
~~~~~~~~~~~~~~~~~~~~

Create a new feature branch and start working on your changes. You can commit
frequently, or use an interactive mode to commit partial changes later. Try to
keep related changes in separate commits, and separate larger code
modifications into multiple commits - this helps with finding out the issues
using :command:`git bisect`. Commits signed by a valid GPG key are preferred.

.. code-block:: console

   git checkout -b new-feature
   # ... work ...
   git add -p .
   # ... pick changes to commit ...
   git commit

Read `How to Write a Git Commit Message <https://chris.beams.io/posts/git-commit/>`_
to learn the best practices about :command:`git` commit messages.

Rewriting history and squashing commits is frowned upon, because this may make
bisecting harder. Small, focused changes are preferable, unless you are
creating a completely new feature, for example a new role; in that case putting
everything in one commit as a starting point is a reasonable approach.

You can add entries about more visible changes or new features to
:file:`CHANGELOG.rst`, but it's not necessary - it will be updated if needed,
before your pull request is merged.

If you notice that you forgot some changes, you can amend your last commit to
include it. If you already pushed your changes to the forked repository on
GitHub, you might need to ``--force`` push your changes again. However, *don't
rewrite history in branches that are already pending as pull requests*.

.. code-block:: console

   # Modify latest commit
   git add -p .
   git commit --amend

Pushing your changes
~~~~~~~~~~~~~~~~~~~~

When your changes are ready, you can push them to your DebOps fork on GitHub.

.. code-block:: console

   git push origin new-feature

After that, go to the upstream DebOps repository page, and create a new pull
request, either against the ``master`` branch, or the stable branch you were
trying to fix. The new pull request will be tested on Travis which might report
errors, and reviewed by DebOps developers, who might request changes. In that
case, you can commit your changes as normal and then push them to your fork on
GitHub, in the same branch. Your pull request will be automatically updated to
reflect new commits.

.. code-block:: console

   # ... Fix issues, add new features ...
   git add -p .
   git commit
   git push origin new-feature

After your pull request is merged, you can fetch the new changes in the
``master`` branch or other branches you worked on, rebase your local clone of
the repository and push them back to your own fork, just as you would with any
other commit from ``upstream``.
Then, you can start working on another feature or bugfix.

How to test your changes
------------------------

Once you push your contribution, Travis CI will run a first round of tests,
mostly related to linting and syntax checking, then will promptly reject your
contribution for the most pedantic reasons imaginable.

In order to avoid this awkward scenario,
you can (and should) run :command:`make test` yourself!

See the `Testing guide <https://docs.debops.org/en/master/developer-guide/testing.html>`_
for more information on installing the tools required
and making the most out of the test suite.

Happy hacking!
