.. _testing:

Testing
=======

Project validation is done using Travis CI.

The actual role and playbook testing is performed by the project developers
using GitLab CI in a locally hosted development environment.


Travis CI
---------

You can easily run the Travis CI suite on your local fork,
by running :command:`make test`.

The :file:`Makefile` includes linting with several different tools,
building the documentation, and testing the project on a docker image.


Software dependencies
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   sudo apt install build-essential git graphviz shellcheck \
                    python3-sphinx python3-sphinx-rtd-theme

   pip install -U pycodestyle nose2 yamllint ansible-lint


If you intend on running :command:`make docker`,
you also need *Docker* and a user able to run docker containers.

Installing Docker Community Edition on Debian involves adding their apt
repository that corresponds to your distro, as described in the
`Docker CE Debian installation instructions`__.

.. __: https://docs.docker.com/install/linux/docker-ce/debian/

You may also want to check out
`Docker CE post-installation steps for linux`__.
For our purposes, all you need is to add your user to the ``docker`` group:

.. __: https://docs.docker.com/install/linux/linux-postinstall/

.. code-block:: console

   sudo usermod -aG docker <username>
   # log out or reboot for this to take effect.


.. _cmd_make_test:

:command:`make test`
~~~~~~~~~~~~~~~~~~~~

Runs all tests. This runs on automatically on contributions on github.


.. _cmd_make_help:

:command:`make help`
~~~~~~~~~~~~~~~~~~~~

Displays all :command:`make` targets, along with a useful description. :)


.. _cmd_make_docker:

:command:`make docker`
~~~~~~~~~~~~~~~~~~~~~~
The test code in :command:`make test` checks if Docker is available, and if not,
this particular test is successfully skipped.

Verifies the Dockerfile and checks if Ansible and DebOps
run fine inside of a Docker container.


.. _cmd_make_docs:

:command:`make docs`
~~~~~~~~~~~~~~~~~~~~

While working with documentation, it can be useful to only run this bit.

The resulting html files will be in :file:`docs/_build/html/`.


.. _cmd_make_links:

:command:`make links`
~~~~~~~~~~~~~~~~~~~~~

Checks the documentation for broken links.
Does not run as part of the Travis CI pipeline.

The script writes its output at :file:`docs/_build/linkcheck/output.txt`.
