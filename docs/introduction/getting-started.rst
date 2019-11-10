.. _getting-started:

Getting Started with DebOps
===========================

.. include:: ../includes/global.rst

Welcome to DebOps!

You have installed `DebOps <installation>` and are wondering where to go next?
Here you can read about creating your first DebOps project and managing remote hosts.

.. contents::
   :local:

An example environment
----------------------

Ansible and DebOps are installed on your workstation or laptop, a so called
"Ansible Controller" - this machine is used to control Ansible and issue
commands. The machine you will configure using DebOps is known as a "remote
host".

DebOps is designed to manage a host from the ground up. A good base
installation is a Debian Stable netinst, with only SSH server enabled and
configured. Everything else will be installed as needed.

.. note::

   If you are using Debian Jessie or other distributions based on it as the
   base install, by default OpenSSH server configured by the installer will
   disallow password authentication on the ``root`` account. You can either
   enable it manually in the :file:`/etc/ssh/sshd_config` file, use public key
   authentication (see 'man authorized_keys' and 'man ssh-copy-id'), or
   configure a separate admin account and use that to bootstrap the host.

An important part of the environment is correctly configured DNS. Some of the
DebOps roles expect a configured domain - it doesn't need to be a real, global
domain, but it should be resolvable by the host. A good way to check if
a remote host has a correctly configured domain is to use the :command:`hostname --fqdn`
command. If the output has at least 1 dot, you should be good to go.

Do not use the domain apex (``example.com``) as the host name - this will
confuse Ansible and leave you with a broken configuration. Instead, create
separate hostnames inside the domain (``server.example.com``), this will be
used by Ansible correctly. It's good to use only one subdomain level per
subnet, this will make wildcard certificates work without issues. If you want,
you can create separate subdomains per subnet.

If your host does not have a domain configured, you will be able to do that
during the bootstrapping process.

In this guide, we will manage an example host called ``server.example.com``.
This host is a virtual machine, and we can connect to it using commands like:

.. code-block:: console

   alice@laptop:~$ ssh root@server.example.com
   alice@laptop:~$ ssh root@server

The ``root`` account requires a password, SSH keys are not installed yet and
there's no administrator account.

Ansible commands are executed on the Ansible Controller from an unprivileged
account ``alice``. This user has an SSH key pair stored in :file:`~/.ssh/id_rsa` or
has its SSH key available in the SSH Agent. An administrator account with the
same name will be created on the remote host during the bootstrap process.

Your first project
------------------

Begin by creating a "DebOps project". It's a directory which contains all of
the data related to a given environment - Ansible inventory, passwords and
other secrets, custom playbooks and roles. To do this, use the ``debops-init``
command:

.. code-block:: console

   alice@laptop:~$ debops-init ~/myproject

This will create a new directory called ``myproject`` and populate it with some
example directories and files. You will perform most of the commands from the
main project directory, so let's ``cd`` into it:

.. code-block:: console

   alice@laptop:~$ cd ~/myproject

Ansible uses a ``hosts`` file to identify hosts that are under its control. In
the project directory this file is located in :file:`ansible/inventory/hosts`. Open
it in your favorite text editor and add the remote host in the main DebOps
host group:

.. code-block:: none

   [debops_all_hosts]
   server    ansible_host=server.example.com

Using a short inventory name allows you to run Ansible commands without
specifying the fully qualified domain name of the host.

Important inventory variables
-----------------------------

Some of the configuration used by DebOps cannot be auto-detected - examples
include IP addresses or network subnets that can connect to a SSH service
remotely, the administrator e-mail account which should receive important
notifications, and so on. Here you can find a list of the most important
variables which, when set correctly in inventory, can save you a trip to the
data center.

To make sure that these variables apply to all hosts in your environment, you
can include them in :command:`ansible/inventory/group_vars/all/` directory. A
common practice is to name the files inside inventory directories after
variable prefixes, separately for each Ansible role. For example, variables
related to :ref:`debops.sshd` role are stored in
:file:`ansible/inventory/group_vars/all/sshd.yml`, variables used by the
:ref:`debops.postfix` role are written in
:file:`ansible/inventory/group_vars/all/postfix.yml`, and so on. The same
scheme can be used in other inventory groups or for separate hosts.

ansible_user
~~~~~~~~~~~~

This is an internal Ansible variable which is used to determine what remote
user account will be used to login to the server. If it's not explicitly set,
Ansible depends on SSH defaults which conventionally use the name of the
current user as the remote username. It's customary to specify this variable
directly in the ``hosts`` file, that way it can be unique for each host:

.. code-block:: none

   [debops_all_hosts]
   server    ansible_ssh_host=server.example.com ansible_user=ansible-admin

In DebOps this variable can be used to change the name of the default
administrator account, it's also used as a primary user account for various
tasks, like database and application administrative accounts.

On a specific platforms you can set this variable to an automatically created
username to make the remote host administration easier:

- Ubuntu-based hosts usually use the ``ubuntu`` username;

- Raspberry Pi / Pi 2 Linux distributions use the ``pi`` user account for this
  purpose;

However, it is advisable to not use the default user accounts, and instead
either create ones based on your own username (the default behavior) or create
completely separate Ansible accounts with administrative access. If you
configure the ``ansible_user`` variable before bootstrapping the host, the
specified username will be used to create an administrator account.

netbase__domain
~~~~~~~~~~~~~~~

If hosts that you want to manage don't have a DNS domain set, or it's incorrect
(for example your VPS provider's domain instead of your own), the
:ref:`debops.netbase` role included in the `DebOps bootstrap playbook`_ can be used to
easily fix that and configure your own domain. By setting this variable to, for
example:

.. code-block:: yaml

   ---
   netbase__domain: 'example.com'

By running the ``debops bootstrap`` command (see further down), your domain
will be configured in the remote hosts' :file:`/etc/hosts` file. Additionally, the
hostname will be changed to the one you specified in the Ansible inventory.
After that is done, it's best to reboot the machine to make sure all of the
changed settings are applied and are persistent.

This variable won't have any effect on hosts that are not "bootstrapped", and
are instead configured using Debian preseeding or LXC templates - these hosts
will presumably get the needed information like hostname and domain from your
own DHCP server.


sshd__whitelist
~~~~~~~~~~~~~~~

Protection of the SSH service is very important. Hosts configured by DebOps use
a firewall and TCP Wrappers to restrict what hosts can connect to it and
automatically block repeated offenders for certain amount of time.

To not block the Ansible Controller, DebOps tries to detect the IP address
from which the connection is made. For the most part it should work as
expected, but if you still are getting blocked, or to be sure that remote
access won't be interrupted, you can define a list of IP addresses or CIDR
subnets that will be allowed to connect to SSH without restrictions.

To do that, in :file:`ansible/inventory/group_vars/all/sshd.yml` add:

.. code-block:: yaml

   ---
   sshd__whitelist: [ '192.0.2.0/24', '2001:db8::/32' ]

This will configure the :ref:`debops.ferm` and
:ref:`debops.tcpwrappers` roles to allow connections to
the :command:`ssh` service from specified networks.

The :ref:`debops.sshd` role has many more variables you can check out to see
the default configuration used by DebOps and what can be changed as needed.

ntp__timezone
~~~~~~~~~~~~~

By default, DebOps does not try to change the remote host timezone and tries to
use the detected one in roles that need that information for the configuration.
If you need to change the timezone, you can do it by setting the
``ntp__timezone`` variable like this:

.. code-block:: yaml

   ---
   ntp__timezone: 'America/New_York'

For UTC timezone, use this format:

.. code-block:: yaml

   ---
   ntp__timezone: 'Etc/UTC'

nullmailer__relayhost
~~~~~~~~~~~~~~~~~~~~~

The default SMTP server used by DebOps is ``nullmailer``. It's a simple,
forward-only Mail Transport Agent which sends all mail to another SMTP server
for processing. It does not provide support for local mail accounts.

By default, ``nullmailer`` will send mail messages to the
``smtp.<your-domain>`` host (it does not support MX record lookups). If this
host doesn't exist, or your local SMTP server has a different address, you can
change it by setting the variable:

.. code-block:: yaml

   ---
   nullmailer__relayhost: 'internal-mx.{{ ansible_domain }}'

Only one relayhost is supported at a time. The specified host should accept
messages from hosts controlled by Ansible for this to work correctly. The SMTP
connections will be encrypted using ``STARTTLS`` command, therefore the SMTP
should use a set of X.509 certificates which are trusted by the host.

The ``nullmailer`` service can be configured to a large extent using the
:ref:`debops.nullmailer` role variables - you can use them to configure SMTP
authentication, use multiple relay servers, and so on.

If you need a more powerful SMTP server, DebOps includes support for Postfix
as well - check the :ref:`debops.postfix` Ansible role.

apt__default_mirrors_lookup, apt__default_sources_lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DebOps tries to detect the operating system a given host is using and configure
it accordingly. Currently selected Debian and Ubuntu releases are recognized
and the package sources for these operating systems should be configured
without issues.

The Raspbian operating system is a little difficult to detect, because Ansible
currently classifies it as "Debian", however its package repositories are
completely different. To avoid issues with incompatible package sources on
your Raspberry Pi/Pi2, you should change the default :ref:`debops.apt`
configuration manually to use the Raspbian repositories. To do that, add these
values in relevant inventory files:

.. code-block:: yaml

   ---
   apt__default_mirrors_lookup: 'raspbian'
   apt__default_sources_lookup: 'raspbian'


Bootstrap a new host
--------------------

.. warning::

  Bootstrapping a host without a configured ``netbase__domain`` will result in
  a broken host configuration.

At this point you most likely have to connect to that host using the ``root``
account and specifying a password. To make that easier, you can use a special
"bootstrap" Ansible playbook to prepare a host for easier management. To do
this, execute the command:

.. code-block:: console

   alice@laptop:~/myproject$ debops bootstrap --limit server --user root --ask-pass

Or, for short:

.. code-block:: console

   alice@laptop:~/myproject$ debops bootstrap -l server -u root -k

This command will execute the `DebOps bootstrap playbook`_ and use it to
install a base set of packages needed by Ansible like ``python`` and
:command:`sudo`, prepare a new administrator account named after your system
user (``alice`` in our example) and allow that account full access to the
``root`` account using :command:`sudo`. Your SSH keys will be installed on
both the ``root`` and administrator accounts.

.. note::

   Bootstrapping a host this way is not needed if you already have an
   administrator account that can use :command:`sudo` without a password. This
   includes hosts configured using Debian Preseed provided by DebOps as well as
   OpenVZ/LXC containers configured using provided templates.

When the `DebOps bootstrap playbook`_ has finished and there are no errors, you can check
if you are able to connect to the server on the administrator account without a
password:

.. code-block:: console

   alice@laptop:~/myproject$ ssh server

After logging in, check if you can run commands using :command:`sudo` without
a password:

.. code-block:: console

   alice@server:~$ sudo -l

Configure the remote host
-------------------------

When a new remote host has been prepared for Ansible management, you can start
the configuration:

.. code-block:: console

   alice@laptop:~/myproject$ debops -l server

This will start the :command:`ansible-playbook` command with the main DebOps
playbook. This by default includes the `DebOps common playbook`_ with a
default set of roles, and any additional playbooks, if they have been enabled.

The initial configuration might take 5-10 minutes on a reasonably fast machine.
There are some steps, like Diffie-Hellman parameter generation, which might
take significantly more time to complete.

When the playbook run has been finished, your remote host should be configured
with:

- a correct set of APT repositories for your operating system release;
- automatic updates of the installed packages with related e-mail messages sent
  to your admin account;
- a set of Diffie-Hellman parameters and SSL certificates ready to use by
  different services (encrypted TLS/SSL connections out of the box);
- configured :command:`iptables`/:command:`ip6tables` firewall and TCP Wrappers;
- enabled network time synchronization as needed;
- a set of useful management software installed on the host (``htop``,
  ``mtr-tiny``, ``mc``, ``vim``, among other things);

Example application - DokuWiki
------------------------------

Each host configured by `DebOps common playbook`_ should have the same set of base
services. After a host is configured, you can enable additional Ansible roles
to install and configure software and applications of your choice.

We will use `DokuWiki <http://dokuwiki.org/>`_ as an example application. The
role that manages the installation is called :ref:`debops.dokuwiki` it uses
:ref:`debops.nginx` and :ref:`debops.php` roles to configure a webserver and
PHP5 environment. The :ref:`debops.nginx` role calls some additional roles,
such as :ref:`debops.ferm` to configure needed services.

To install DokuWiki on your new remote host, you need to enable the respective
role in Ansible inventory. This is done by creating a new host group,
``[debops_service_dokuwiki]`` in the ``hosts`` file, and adding the desired
hosts to it:

.. code-block:: none

   [debops_all_hosts]
   server    ansible_ssh_host=server.example.com

   [debops_service_dokuwiki]
   server

As you can see, you don't need to copy the whole host entry, only the short
name is enough.

The :ref:`debops.dokuwiki` role has many default variables you can use to
customize the installation. One of the more useful ones is
``dokuwiki_main_domain``; it's a list which specifies what DNS subdomains are
used to access the wiki (each application in the DebOps set of roles is
configured on a separate subdomain). By default DokuWiki will be accessible on
the ``wiki.{{ ansible_domain }}`` subdomain, if you want to change it, you can
do so by creating the :file:`ansible/inventory/host_vars/server/dokuwiki.yml`
configuration file and specifying the subdomain(s) in it:

.. code-block:: yaml

   ---
   dokuwiki__fqdn: 'wiki.{{ ansible_domain }}'

Remember that the chosen subdomain (``wiki.`` or your own) needs to be
configured in your DNS server to point to the specified remote host.

When everything is configured, you can execute the ``debops`` script to apply
new configuration on the host:

.. code-block:: console

   alice@laptop:~/myproject$ debops -l server

This will apply the whole playbook with all the configuration on the specified
server. However, to make this process faster, DebOps provides separate "service
playbooks" for each of the roles. To use these playbooks, you can specify them
as the first argument to the ``debops`` command:

.. code-block:: console

   alice@laptop:~/myproject$ debops service/dokuwiki -l server

This will tell the script to look for the playbook in several places:

- :file:`playbooks/` and :command:`ansible/playbooks/` subdirectories in the project
  directory;
- :file:`debops-playbooks/playbooks/` subdirectory of the project directory, if
  DebOps playbooks and roles are installed inside of it;
- :file:`~/.local/share/debops/debops-playbooks/playbooks/` directory (default
  install location);

The first one found will be executed. You can use this to your advantage by
adding custom playbooks in :file:`playbooks/` or :command:`ansible/playbooks/`
directories, they need to be named with ``.yml`` extension. Custom roles can
be placed in the :file:`roles/` or :command:`ansible/roles/` subdirectories located in the
project directory.

After Ansible finishes the configuration, you will need to go to the
``https://wiki.<domain>/install.php`` page to complete the installation
process.

At this time you might find that the web browser you are using does not
recognize the CA certificates served by the host. This happens when the server uses
certificates signed by internal DebOps Certificate Authority instead of the
"regular" ones. To fix that, consult the :ref:`debops.pki` role documentation (when it's available).

Where to go from here
---------------------

You can add more hosts to the Ansible inventory and configure them in a cluster.
Hosts should automatically trust each other using an internal Certificate
Authority, so encrypted connections between them should work out of the box.

DebOps contains multiple Ansible roles that allow you to install and configure
useful software, like GitLab, phpIPAM, ownCloud and others. You should check
`the documentation <https://docs.debops.org/>`_ of the respective roles to see
some example configurations and useful tips. Note that parts of the
documentation are currently outdated - if a given role has only one page, you
should check the role files directly.

You can check the :ref:`DebOps Changelog <changelog>` for updates
related to roles and playbooks (there's also an `Atom feed
<https://log.debops.org/atom.xml>`_ available for your feed reader).

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
