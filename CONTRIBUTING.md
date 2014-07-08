## Contributing to ginas

ginas is currently maintained by [Maciej Delmanowski](https://github.com/drybjed).
It's a personal project, currently in heavy development. Usage in production is
encouraged but at the moment it should be limited - main parts of the code might
be refactored and changes might not be backwards-compatible.

### Development guidelines

ginas is written and used with [Ansible](https://github.com/ansible/ansible/)
`devel` branch. New Ansible updates are applied daily and any bugs that result
are found and reported to Ansible issue tracker. Usage of `devel` Ansible
branch allows ginas to use newest changes and modules available in the project,
at the cost of compatibility with current stable version of Ansible.

ginas uses [Debian GNU/Linux](https://debian.org/) as the base operating system
with [Debian Stable](https://www.debian.org/releases/stable/) as the main
distribution.

Other Linux distributions based on Debian, like [Ubuntu](http://ubuntu.com/)
are not officially supported. An effort is made to keep ginas compatible with
current Ubuntu LTS release (12.04) which is used on [Travis CI](https://travis-ci.org/)
servers, but not all functions of the playbook are working due to old packages
and extensive changes required on the target system.

New servers based on ginas should be installed using minimal Debian install,
preferably [Debian netinst (amd64)](https://www.debian.org/CD/netinst/) with only SSH
server installed for remote access. ginas supports both physical servers and
virtual machines.

Development of the playbook occurs in users private git repositories, finished
code is then pulled via pull requests to [main ginas repository](https://github.com/ginas/ginas/).
New pull requests are [built on [Travis CI](https://travis-ci.org/ginas/ginas/)
and checked for errors. If a pull request results in an error, changes are applied
until such time that merge will be successful - whether fixes are needed in
ginas playbook, or Ansible.

If you want to contribute code, you should fork ginas to your own repository
and work there. You should use `git rebase` to keep your repository updated.

### Contribution work flow

1. [Fork ginas](https://github.com/ginas/ginas/fork) to your github account
2. Clone your fork onto your workstation
  - `git clone git@github.com:yourname/ginas.git`
3. Add ginas/ginas to the upstream
  - `git remote add upstream https://github.com/ginas/ginas/`

#### Make sure your repo is always updated

You will always want to perform these steps before making any changes:

1. `git checkout master`
2. `git fetch upstream`
3. `git rebase upstream/master`
4. `git push origin master`

#### Make your contribution

1. `git checkout -b yourfeaturebranch`
2. `git add <insert your files to add>`
3. `git push origin yourfeaturebranch`
4. Goto your forked repo on github
  - Select your feature branch
  - Click the pull request icon next to the branch
  - Follow github's instructions and create the pull request
5. `git checkout master`
  - At this point you are free to make any other feature branches for future pull requests

### Public API, Versioning and stable releases

ginas uses [Semantic Versioning](http://semver.org/) specification for stable
releases. Public API in ginas consists of:
- all information that can be configured using Ansible inventory:
  * any variables defined in `role/defaults/main.yml` files,
  * any variables used to communicate between different roles via dependencies,
  * any data accessed via `lookup()` functions,
- any custom modules, callbacks, plugins and other similar files provided with
  playbook and not included in Ansible itself,
- any scripts and other executable data outside of the main playbook.

Before version 1.0.0 is released, ginas public API should be considered
unstable. During this development cycle, minor version releases (0.x.0) will be
incremented when major public API changes are introduced:
- default variables in roles are removed or renamed,
- mechanisms used to communicate between roles via dependencies are changed,
- command options of outside scripts are changed or scripts are removed,
- definition of public API is changed,
- etc.

Patch version releases (0.0.x) will be incremented when new roles are
introduced, or roles are modified without affecting backwards compatibility of
the public API (for example new default variables are introduced). On the new
minor release, patch version number will be reset to 0.

After 1.0.0 version is released, ginas public API should be considered stable
and above conventions should be updated to comform with Semantic Versioning:
major public API changes should increment major version number (x.0.0), new
public API default role variables, new roles or modifications to roles
should increment minor version number (0.x.0). Bugfixes to stable releases
should increment patch version number (0.0.x) and should be applied on
a separate git branch.

### Communication channels and support

At the moment ginas has no official homepage. Official git repository can be
found on [GitHub](https://github.com/ginas/ginas/).  Issues and pull requests
should be posted in the [issue tracker](https://github.com/ginas/ginas/issues?state=open)
of main ginas repository.

There is an official IRC channel, `#ginas` on FreeNode IRC network. You can
also find author and users of ginas on official Ansible channel, `#ansible` on
FreeNode.

You can use public mailing list,
[ginas-users](https://groups.google.com/forum/#!forum/ginas-users), for
official discussion about the project.

### License and copyright

Official license used in ginas is [GNU General Public License v3](https://www.gnu.org/copyleft/gpl.html),
the same as the Ansible project ginas is based on. Contributed code should be
licensed on the same license as main project, or a
[compatible license](https://stackoverflow.com/questions/1978511/is-there-a-chart-of-which-oss-license-is-compatible-with-which).

