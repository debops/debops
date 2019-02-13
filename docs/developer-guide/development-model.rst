Development model
=================

The DebOps project uses an Open Source, distributed development model. The
`main code repository`__ is located on GitHub, repository forks are used to
introduce and test new code which is then later merged into the main monorepo.

.. __: https://github.com/debops/debops/

This is a basic code flow from the developers, through the DebOps monorepo and
to the end users:

.. graphviz::

   digraph DebOps {

       // Project maintainer
       drybjed [label="@drybjed" shape="plaintext"];

       // Contributors
       contributors [label="Contributors" shape="plaintext"];

       monorepo [style="filled" fillcolor="limegreen" shape="Mrecord" label="<pr> Pull Requests|<code> github.com/debops/debops"];
       gitlab_mirror [style="filled" fillcolor="orange2" shape="record" label="gitlab.com/debops/debops"];
       gitlab_drybjed_local [style="filled" fillcolor="darkgoldenrod2" shape="record" label="gitlab.local/drybjed/debops"];
       drybjed_make_test [shape="diamond", style="rounded,filled" fillcolor="tomato2" label="make test"];
       monorepo_drybjed_local [shape="record" style="filled" fillcolor="mediumseagreen" label="<pull> Pulls |<code> ~/src/debops/debops"];

       travis_ci [label="Travis CI" shape="diamond" style="rounded,filled" fillcolor="tomato2"];
       docker_hub [label="Docker Hub" style="filled" fillcolor="deepskyblue3"];
       readthedocs [label="ReadTheDocs" style="filled" fillcolor="slategray4"];
       pypi [label="PyPI" style="filled" fillcolor="steelblue3"];
       gitlab_runner [label="GitLab Runners" shape="diamond" style="rounded,filled" fillcolor="lightseagreen"];

       fork_drybjed_local [shape="record" style="filled" fillcolor="skyblue1" label="<code> ~/src/drybjed/debops"];
       fork_drybjed_github [shape="record" style="filled" fillcolor="khaki1" label="<code> github.com/drybjed/debops"];

       fork_devel_local  [shape="record" style="filled" fillcolor="skyblue1" label="<code> ~/src/devel/debops"];
       fork_devel_github [shape="record" style="filled" fillcolor="khaki1" label="<code> github.com/devel/debops"];
       devel_make_test [shape="diamond", style="rounded,filled" fillcolor="tomato2" label="make test"];

       { rank="source" drybjed, contributors }
       { rank="same" fork_drybjed_local, monorepo_drybjed_local, fork_devel_local }
       { rank="sink" docker_hub, readthedocs, pypi }

       drybjed              -> fork_drybjed_local [color="coral3" fontcolor="coral3" label="Local development"];
       fork_drybjed_local   -> gitlab_drybjed_local [color="coral3" fontcolor="coral3" label="New commits"];
       gitlab_drybjed_local -> gitlab_runner [color="lightseagreen" fontcolor="lightseagreen" label="Role tests"];
       fork_drybjed_local   -> drybjed_make_test [color="coral3" fontcolor="coral3" label="Local tests"];
       drybjed_make_test    -> fork_drybjed_github [color="coral4" fontcolor="coral4" label="New commits"];
       fork_drybjed_github  -> monorepo:pr [color="coral4" fontcolor="coral4" label="New PRs"];

       contributors         -> fork_devel_local [color="dodgerblue2" fontcolor="dodgerblue2" label="Local development"];
       fork_devel_local     -> devel_make_test [color="dodgerblue2" fontcolor="dodgerblue2" label="Local tests"];
       devel_make_test      -> fork_devel_github [color="dodgerblue4" fontcolor="dodgerblue4" label="New commits"];
       fork_devel_github    -> monorepo:pr [color="dodgerblue4" fontcolor="dodgerblue4" label="New PRs"];

       fork_devel_github    -> fork_drybjed_local -> gitlab_drybjed_local [style="dashed" color="coral3" fontcolor="coral3" label="Integration pulls"];

       monorepo:pr -> travis_ci [dir="both" color="tomato2" fontcolor="tomato2" label="PR tests"];

       monorepo:pr -> monorepo_drybjed_local:pull -> drybjed [color="darkgreen" fontcolor="darkgreen" label="Approved PRs"];
       drybjed -> monorepo_drybjed_local:code [color="purple" fontcolor="purple" label="Code signing"];
       monorepo_drybjed_local:code -> monorepo:code [color="purple" fontcolor="purple" label="Signed merges"];

       monorepo:code -> docker_hub [color="deepskyblue3" fontcolor="deepskyblue3" label="Docker image"];
       monorepo:code -> readthedocs [color="slategray4" fontcolor="slategray4" label="Documentation"];

       monorepo_drybjed_local:code -> pypi [color="steelblue3" fontcolor="steelblue3" label="Signed Python package"];

       monorepo:code -> gitlab_mirror [color="orange2" fontcolor="orange2" label="Code mirror"];
       gitlab_mirror -> gitlab_runner [color="lightseagreen" fontcolor="lightseagreen" label="Role tests"];
   }

The green rectangles represent the DebOps monorepo (on GitHub) and its local
clone on the project maintainer's workstation where GPG code signing is
performed.

The yellow rectangles represent monorepo forks on GitHub, which are cloned to
the local :command:`git` repositories, shown in blue. Local development is
performed there, developers can use the :command:`make test` command to check
if the code passes the tests (code linting; the same tests are performed on all
pull requests using Travis CI).

A separate test infrastructure based on GitLab and GitLab Runners can be used
to test DebOps roles and playbooks directly. This is done locally by the
project maintainer during development. Larger PRs from other contributors can
also be pulled to check the changes in the roles and for general integration
tests. Signed and accepted pull requests are also tested using GitLab, via
a mirror of the DebOps monorepo. Contributors can also set up their own local
GitLab environment to perform role and playbook tests.

New commits in the DebOps monorepo trigger the automatic rebuild of the
official DebOps Docker image and rebuild of the documentation on ReadTheDocs.
New project releases are published manually in PyPI using signed Python
packages.
