## [![DebOps project](http://debops.org/images/debops-small.png)](http://debops.org) roundcube

[![Travis CI](http://img.shields.io/travis/debops-contrib/ansible-roundcube.svg?style=flat)](http://travis-ci.org/debops-contrib/ansible-roundcube)
[![test-suite](http://img.shields.io/badge/test--suite-ansible--roundcube-blue.svg?style=flat)](https://github.com/ganto/test-suite/tree/master/ansible-roundcube/)
[![Platforms](http://img.shields.io/badge/platforms-debian-lightgrey.svg?style=flat)](#)

### Warning, this is a Beta role

This role has been marked by the author as a beta role, which means that it
might be significantly changed in the future. Be careful while using this role
in a production environment.

***

This role installs and manages [Roundcube](http://roundcube.net/), a IMAP Web
client written in PHP.

### Installation

This role requires at least Ansible `v1.8.0`. To install it, clone it
to your [DebOps](http://debops.org) project roles directory:

```Shell
git clone http://github.com/debops-contrib/ansible-roundcube.git
```

### Are you using this as a standalone role without DebOps?

You may need to include missing roles from the [DebOps common
playbook](https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml)
into your playbook.

[Try DebOps now](https://github.com/debops/debops) for a complete solution to run your Debian-based infrastructure.


### Role dependencies

* ``debops.secret``

* ``debops.nginx``

* ``debops.php5``

* ``debops.mariadb``


### Authors and license

`roundcube` role was written by:

- [Reto Gantenbein](https://linuxmonk.ch/) | [e-mail](mailto:reto.gantenbein@linuxmonk.ch) | [GitHub](https://github.com/ganto)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)
