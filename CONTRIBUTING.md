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

