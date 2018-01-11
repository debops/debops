How to contribute to DebOps
===========================

This file explains how you can contribute to the DebOps project.


Code contributions
------------------

Pull requests welcome
~~~~~~~~~~~~~~~~~~~~~

DebOps is primarly developed using GitHub pull requests. After forking the main
project repository to your own GitHub account, you should create a branch for
a new feature or a bugfix; this helps separate your work on different parts of
the repository. You can read the `DEVELOPMENT.rst <https://github.com/debops/debops/blob/master/DEVELOPMENT.rst>`__
file for tips about managing your forked repository and committing code.


GPG-signed commits are preferred
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project is developed using a distributed model, and its code is used on
``root`` account in production environments. Because of that, DebOps developers
rely on GPG-signed :command:`git` commits to ensure authenticity of the code
included in the project. Commits without proper GPG signatures will still be
accepted for the time being, to allow the contributors to transition to
a GPG-signing workflow over time.


Issues or feature requests
--------------------------

GitHub issues
~~~~~~~~~~~~~

The project's `issue page <https://github.com/debops/debops/issues>`__ on
GitHub can be used to report issues with the code or request new features. If
you have a potential feature already written, you can directly create a pull
request without a separate issue, it will be discussed and reviewed on the pull
request page.


General discussion
------------------

Project's mailing list
~~~~~~~~~~~~~~~~~~~~~~

The DebOps project has `a mailing list <https://lists.debops.org/mailman/listinfo/debops-users>`__
which can be used for general discussion about the project, issue reporting,
etc. The list is also used for announcements concerning the project as a whole.
If you plan to use DebOps in your environment, you should subscribe to this
mailing list, it's relatively low volume.

#debops IRC channel
~~~~~~~~~~~~~~~~~~~

The project maintainers and users hang out on the ``#debops`` IRC channel in
the FreeNode network. You can come over for a more real-time discussion or for
support questions.
