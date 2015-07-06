This [Ansible](http://ansible.com/) role allows you to install and manage
[Roundcube](http://roundcube.net/), a IMAP Web client written in PHP.


### Installation

This role requires at least Ansible `v1.7.0`. To install it, clone it
to your [DebOps](http://debops.org) project roles directory:

    git clone http://github.com/ganto/ansible-roundcube.git


### Role dependencies

* ``debops.secret``

* ``debops.nginx``

* ``debops.php5``

* ``debops.mysql``


### Authors and license

`roundcube` role was written by:
- Reto Gantenbein | [e-mail](mailto:reto.gantenbein@linuxmonk.ch) | [GitHub](https://github.com/ganto)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)
