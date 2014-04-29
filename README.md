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
  [Mailman](http://list.org/), with more to come;

### Screenshots

It's hard to create a screenshot of what Linux server really looks like, so
instead here you can see a gallery of what Ansible roles are currently
included in ginas and what's their relationship with each other. Below you can
see a basic structure of the main ginas playbook (click on the image to see
it in full size):

[![ginas at a glance](http://i.imgur.com/hKhet35.png)](http://i.imgur.com/hKhet35.png)

Next graph shows Ansible role dependencies, represented by dashed lines. Here
you can see what roles depend on each other. Dependencies of a role are
executed before that role, and certain roles can be run multiple times by
Ansible:

[![ginas role dependencies](http://i.imgur.com/BM0yGHL.png)](http://i.imgur.com/BM0yGHL.png)

