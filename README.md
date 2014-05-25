## ginas is not a server

[![Travis CI](https://travis-ci.org/ginas/ginas.png?branch=master)](https://travis-ci.org/ginas/ginas) [![Flattr this project](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=drybjed&url=https://github.com/ginas/ginas/&title=ginas&language=&tags=github&category=software)

ginas is a set of [Ansible](http://ansible.com/) playbooks designed to create
and maintain a datacenter based on [Debian GNU/Linux](http://debian.org/)
operating system. It is designed to be very flexible and automatically adapt
to whatever environment you throw at it - whether these are real, hardware
servers, KVM / VirtualBox / VMWare virtual machines, or OpenVZ / LXC
containers - ginas should manage them just as easily.

### Features

- low-level server management - iptables firewall (using
  [ferm](http://ferm.foo-projects.org/)), network interfaces with optional NAT,
  tcpwrappers, basic user management, its own implementation of PKI certificate
  infrastructure, optional support for SSH authentication with
  [Monkeysphere](http://monkeysphere.info/);

- advanced package management using APT, with ability to maintain local
  package cache (using apt-cacher-ng), create local APT repository with
  reprepro, maintain security updates with unattended-upgrades and apticron;

- basic set of services: nginx web server, MySQL and PostgreSQL database
  servers, [SKS](http://www.keysigning.org/sks/) OpenPGP/GPG key server, DNSmasq
  DNS/DHCP/PXE server, NFS server and client, Samba file server, Postfix mail
  server;

- set of fully-fledged applications: [ownCloud](http://owncloud.org/),
  [phpIPAM](http://phpipam.net/), [GitLab](http://gitlab.org/),
  [GitLab CI](https://www.gitlab.com/gitlab-ci/),
  [Mailman](http://list.org/), [Etherpad](http://etherpad.org/),
  with more to come;

### Screenshots

It's hard to create a screenshot of what Linux server really looks like, so
instead here you can see a gallery of what Ansible roles are currently
included in ginas and what's their relationship with each other. Below you can
see a basic structure of the main ginas playbook (click on the image to see
it in full size):

[![ginas at a glance](http://i.imgur.com/4fsJiRI.png)](http://i.imgur.com/4fsJiRI.png)

Next graph shows Ansible role dependencies, represented by dashed lines. Here
you can see what roles depend on each other. Dependencies of a role are
executed before that role, and certain roles can be run multiple times by
Ansible:

[![ginas role dependencies](http://i.imgur.com/SnptafZ.png)](http://i.imgur.com/SnptafZ.png)

### Other projects of unusual size

If you like the concept of a giant, general-purpose playbooks, but you don't
necessarily like this particular implementation, I suggest that you check out
other similar projects:

- [al3x/sovereign](https://github.com/al3x/sovereign): an orginal inspiration
  for ginas, playbook with multiple services focused on privacy and personal
  freedom. Based on [Debian 7](https://www.debian.org/releases/wheezy/)

- [edx/configuration](https://github.com/edx/configuration): allows you to
  create and manage an instance of [Open edX platform](http://code.edx.org/).
  Focused on AWS and cloud services. Based on [Ubuntu
  12.04](http://releases.ubuntu.com/12.04/)

- [iceburg-net/ansible-pcd](https://github.com/iceburg-net/ansible-pcd):
  Ansible provisioning and deployment framework, inspired by Open edX
  project. Based on [Debian 7](https://www.debian.org/releases/wheezy/)

- [jnv/ansible-fedora-infra](https://github.com/jnv/ansible-fedora-infra):
  cloud infrastructure for Fedora Project, focused on Amazon/AWS services.
  Based on [Fedora](https://fedoraproject.org/)

- [pjan/the-ansibles](https://github.com/pjan/the-ansibles): collection of
  Ansible roles which can be used to build a Cloudbox, similar to Sovereign.
  Based on [Ubuntu 12.04](http://releases.ubuntu.com/12.04/)

If you have or know a project that is not on the list and has similar scope,
please let me know!

