# [![DebOps logo][debops-logo]](https://debops.org/) DebOps

*Your Debian-based data center in a box*

[![GitHub CI][github-ci]](https://github.com/debops/debops/actions?query=workflow%3A%22Continuous+Integration%22)
[![GitLab CI][gitlab-ci]](https://gitlab.com/debops/debops/pipelines)
[![CII Best Practices][cii-best-practices]](https://bestpractices.coreinfrastructure.org/en/projects/237)
[![REUSE status][reuse-status]](https://api.reuse.software/info/github.com/debops/debops)
[![RSS commits][rss-commits]](https://github.com/debops/debops/commits/master.atom)

[debops-logo]: https://raw.githubusercontent.com/debops/debops/master/lib/images/debops-small.png
[github-ci]: https://github.com/debops/debops/workflows/Continuous%20Integration/badge.svg
[gitlab-ci]: https://gitlab.com/debops/debops/badges/master/pipeline.svg
[cii-best-practices]: https://bestpractices.coreinfrastructure.org/projects/237/badge
[reuse-status]: https://api.reuse.software/badge/github.com/debops/debops
[rss-commits]: https://img.shields.io/badge/RSS-commits-orange.svg


The DebOps project provides a set of general-purpose [Ansible][ansible] roles
that can be used to manage [Debian][debian] or [Ubuntu][ubuntu] hosts. In
addition, a default set of Ansible playbooks can be used to apply the provided
roles in a controlled way, using Ansible inventory groups.

[ansible]: https://github.com/ansible/ansible/
[debian]: https://www.debian.org/
[ubuntu]: https://www.ubuntu.com/

The roles are written with a high customization in mind, which can be done
using Ansible inventory. This way the role and playbook code can be shared
between multiple environments, with different configuration in to each one.

Services can be managed on a single host, or spread between multiple hosts.
DebOps provides support for different SQL and NoSQL databases, web servers,
programming languages and specialized applications useful in a data center
environment or in a cluster. The project can also be used to deploy
virtualization environments using KVM/libvirt, Docker or LXC technologies to
manage virtual machines and/or containers.

You can find out more about DebOps features on the [project's documentation
page][debops-docs].

[debops-docs]: https://docs.debops.org/


## Quick start

Start a Docker container which acts as an Ansible Controller host with DebOps
support, based on Debian Buster:

    docker run -it --rm debops/debops
    cd src/controller ; debops run common --diff

Or, create a Vagrant VM which acts as an Ansible Controller host:

    git clone https://github.com/debops/debops
    cd debops && vagrant up && vagrant ssh
    cd src/controller ; debops run common --diff

You can use configuration in the `src/controller` subdirectory to try out
DebOps against the container/VM, or create your own DebOps project directory
using `debops project init` command.

More quick start tips can be found [in the DebOps quick start guide][quick-start].

[quick-start]: https://docs.debops.org/en/master/introduction/quick-start.html


Installation
------------

You can install the [DebOps Python package][debops-pypi], which includes the
DebOps roles and playbooks, as well as additional scripts which can be used to
setup separate project directories and run Ansible in a convenient way. To
install the Python package with Ansible and other required dependencies, run
the command:

    pipx install --user debops[ansible]

[debops-pypi]: https://pypi.org/project/debops/

Alternatively, DebOps roles are available on [Ansible Galaxy][debops-galaxy]
as an Ansible Collection which can be installed using the `ansible-galaxy`
command:

    ansible-galaxy collection install debops.debops

[debops-galaxy]: https://galaxy.ansible.com/debops/debops/

Read the [installation instructions][install] in the DebOps documentation for
more details about required software and dependencies.

[install]: https://docs.debops.org/en/master/introduction/install.html


## Getting started

Ansible uses SSH to connect to and manage the hosts. DebOps enforces the SSH
security by disabling password authentication, therefore using SSH keys to
connect to the hosts is strongly recommended. This can be changed using the
inventory variables.

During initial deployments you might find that the firewall created by DebOps
blocked you from accessing the hosts. Because of that it's advisable to have an
out-of-band console access to the host which can be used to login and
troubleshoot the connection.

Create a new environment within a DebOps "project directory", add some hosts in
the Ansible inventory and run the default DebOps playbook against them to
configure them:

    # Create a new environment
    debops project init ~/src/projects/my-environment
    cd ~/src/projects/my-environment

    # Modify the 'ansible/inventory/hosts' file to suit your needs, for example
    # uncomment the local host to configure it with DebOps

    # Run the full playbook against all hosts in the inventory
    debops run site

    # Run the common playbook against specific host in the inventory
    debops run common -l <hostname>

You should read the [Getting Started with DebOps][getting-started] guide for
a more in-depth explanation of how the project can be used to manage multiple
hosts via Ansible.

[getting-started]: https://docs.debops.org/en/master/introduction/getting-started.html


Development
-----------

Create [a fork of this repository][debops-fork] and clone it to your
workstation. Create a development DebOps environment and symlink the forked
repository in it. Now you can create new playbooks/roles in the forked
repository and see their results in the development environment.

    git clone git@github.com:<username>/debops ~/src/github.com/<username>/debops
    cd ~/src/github.com/<username>/debops
    git remote add upstream https://github.com/debops/debops.git

    debops project init ~/src/projects/debops-devel
    cd ~/src/projects/debops-devel
    ln -s ~/src/github.com/<username>/debops debops

You can pull latest changes to the project from the upstream repository:

    cd ~/src/github.com/<username>/debops
    git checkout master
    git fetch upstream
    git rebase upstream/master

Read the [development guide][devel-guide] file for more details about the
DebOps development process.

[devel-guide]: https://docs.debops.org/en/master/developer-guide/contribution-workflow.html


## Contributing

DebOps development is done via a distributed development model. New features
and changes are prepared in a [fork of the official repository][debops-fork]
and are published to the original repository via GitHub pull requests. PRs are
reviewed by the DebOps developer team and if accepted, are merged in the main
repository.

[debops-fork]: https://github.com/debops/debops/fork

GPG-signed `git` commits are preferred to ensure authenticity.

Read the [contributing guide][contrib-guide] file for more details about how to
contribute to DebOps.

[contrib-guide]: https://docs.debops.org/en/master/developer-guide/contributing.html


## Licensing

The DebOps project is licensed under the [GNU General Public License 3.0 or later][GPL-3.0-or-later].
You can find full text of the license in the [LICENSES/GPL-3.0-or-later.txt] file.

Some files included with the DebOps project use a different license.
The licenses are marked in these files using the [SPDX license identifiers][spdx-ids]
and can be found in the `LICENSES/` subdirectory. They are also included in the
project tarballs, Ansible Collections and Python packages. The project uses the
[REUSE Specification][reuse-specification] and its associated tool to check and
verify copyright and license information in all files.

[GPL-3.0-or-later]: https://www.gnu.org/licenses/gpl-3.0
[LICENSES/GPL-3.0-or-later.txt]: https://github.com/debops/debops/blob/master/LICENSES/GPL-3.0-or-later.txt
[spdx-ids]: https://spdx.org/ids
[reuse-specification]: https://reuse.software/spec/
