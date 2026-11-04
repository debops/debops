.. Copyright (C) 2019 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2019-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

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

   pip install -U pycodestyle pytest pytest-cov yamllint ansible-lint reuse


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


.. _cmd_make_test_unit:

:command:`make test-unit`
~~~~~~~~~~~~~~~~~~~~~~~~~

Runs the unit tests for the :command:`debops` Python package using pytest,
together with a coverage report. The tests live in :file:`src/tests/unit/`;
each module of the package has a matching :file:`test_*.py` file. External
tools are replaced with test doubles, so the suite runs the same way on any
machine.


.. _cmd_make_test_integration:

:command:`make test-integration`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs the integration tests from :file:`src/tests/integration/`, which drive
the real :command:`debops` command line in temporary directories: project
initialization, command dispatch and secret management. Tests which need
optional tools such as :command:`ansible-inventory`, :command:`git-crypt` or
:command:`encfs` are skipped when the tools are not installed.


.. _cmd_make_test_coverage:

:command:`make test-coverage`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs the unit and integration tests together and prints a combined coverage
report. Use this to see the real coverage of the modules which the
integration tests exercise, for example the project directory management;
the unit-only report of :command:`make test-unit` understates them.


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


.. _testing_mutation:

Mutation testing
----------------

Code coverage tells you which lines the test suite executes. Mutation testing
tells you which lines the test suite actually validates. The `mutmut`__ tool
generates small mutations of the :file:`src/debops/` sources — flipped
comparisons, changed constants, removed statements — and runs the tests
against each mutant. A mutant that *survives* means the suite passes with
broken code: a gap in the assertions.

.. __: https://mutmut.readthedocs.io/

Run it locally with:

.. code-block:: console

   mutmut run

A full pass over the package generates around 11k mutants and takes a few
minutes on a typical workstation. Review the results with
:command:`mutmut results`, and inspect an individual mutant with
:command:`mutmut show <mutant-id>`. The configuration lives in the
``[tool.mutmut]`` section of :file:`pyproject.toml`.

A few things to keep in mind when reading the results:

- Integration tests are excluded from the mutation loop. They drive the real
  :command:`debops` command line in subprocesses, which cannot see the
  mutated code, so they would always pass regardless of the mutations.
- Surviving mutants in code that only builds :command:`git` or
  :command:`ansible-playbook` command lines are expected. The interesting
  findings are in the logic modules: configuration handling, inventory
  parsing, version comparison.
- The goal is not a 100% mutation score. Triage the survivors, fix the
  assertion gaps that matter, and accept the rest.

The :file:`mutants/` directory created during a run is a scratch copy of the
project used to apply the mutations. It is ignored by Git and can be removed
at any time.
