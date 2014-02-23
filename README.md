# ginas

[![Travis CI](https://travis-ci.org/drybjed/ginas.png?branch=devel)](https://travis-ci.org/drybjed/ginas)

ginas is not a server, it's an entire datacenter defined in [Ansible](http://ansibleworks.com/) playbooks and built using [Debian](http://debian.org/) operating system. With ginas, you can configure your servers in minutes and easily rebuild them if you want to.

## Main features

Here's list of already implemented features in ginas. Project is currently in an early stages of development, and it's not yet ready for serious production environment, but it's certainly headed in that direction.

### Autoconfiguration

Install and configure [Debian Stable](http://www.debian.org/releases/stable/) servers with almost no prior configuration. Only requirement is preparation of [Ansible inventory](http://www.ansibleworks.com/docs/intro_inventory.html) with list of hosts to manage, almost everything else is then automatically created for you (passwords, SSL certificates, databases).

### Easy customization

[Ansible roles](http://www.ansibleworks.com/docs/playbooks_roles.html) used in ginas can be easily customized using inventory variables. You can use the same ginas playbook in completely different environments, or even manage multiple datacenters from one central location, with options like local APT repositories or proxy servers customized for each datacenter.

### Encrypted storage for sensitive information

ginas can create an encrypted secret storage on Ansible controller (host which runs Ansible playbooks), and automatically decrypt it during configuration phase and close it afterwards. Encrypted storage is created using [cryptsetup + LUKS](https://code.google.com/p/cryptsetup/), and can be protected using passphrases or [GnuPG](http://gnupg.org/) keys. With secret storage enabled, ginas can automatically generate passwords, SSL certificates with keys, and other sensitive information, and store it securely on your machine, which can then be disconnected from the network after configuration phase is finished.

### Server backup and restore

Critical information about servers (SSH host keys, monkeysphere keyring, SSL certificates) can be easily backed up before destruction of a server and restored after reinstall (and before main configuration), to keep [server identity](http://web.monkeysphere.info/doc/host-keys/) intact. Note: this is not a full server backup solution.

## Implemented services

- **Debian Installer**: install Debian servers using PXE boot and prepre them for Ansible deployment using preseeding

- **apt**: management of Debian APT repositories, automatic upgrades using `unattended-upgrades`, centralized cache for packages using `apt-cacher-ng`

- **git hosting**: simple git repository hosting with SSH access

- **KVM and LXC**: you can configure hosts to support [KVM](http://www.linux-kvm.org/) virtual machines and [Linux Containers](http://linuxcontainers.org/) (even LXC inside KVM), which then can be configured using *the same playbook*

- **monkeysphere**: all servers configured using ginas can use [monkeysphere](http://web.monkeysphere.info/) project to securely and reliably manage access to SSH using GnuPG keys and OpenPGP Web of Trust. Each host can automatically publish its public key, which can then be signed by an administrator. During initial configuration, ginas can automatically import selected PGP keys as trusted certifiers and automatically grant access to configured user accounts. You can also install and configure your own internal keyservers using [sks](http://www.keysigning.org/sks/) which can optionally be connected to public keyserver network.

- **pki**: each server creates its own set of SSL certificates and keys, automatically self-signed. In addition, each certificate is accompanied by certificate request automatically sent to Ansible controller. Using that request you can sign host certificates using your own CA (or an external CA) and automatically publish signed certificates back to servers.

- **dnsmasq**: simple DNS and DHCP for local network, great for local development environment - forget using IP addresses, use hostnames for your development servers

- **ferm**: easy to use iptables management script, which is integrated with other services managed using ginas

- **nginx**: main webserver used in ginas, with configuration defined using YAML lists and hashes. By default configured with strong TLS/SSL encryption in mind.

- **mysql**: install and configure MySQL databases, with automated backups using automysqlbackup

- **php5-fpm**: support for [php5-fpm](http://php-pfm.org/) pools, which can then be easily configured in nginx as upstreams, either local with sockets or remote with TCP ports

- **nfs**: share directories across network using NFS

- **tcpwrappers**: protect services from unauthorized access, optionally with [denyhosts](http://denyhosts.sourceforge.net/)

- **user management**: define different types of user accounts (administrators, users with SSH access, restricted accounts with sftponly or git-shell access) and automatically create them using Ansible

