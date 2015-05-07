Getting Started
====================


Your first project
------------------

**Set up your first project**

::

   $ debops-init ~/myproject
   $ cd ~/myproject

**Add a host to your inventory**

Enter your hosts into ``ansible/inventory/hosts``. For the beginning
we suggest entering one server only so you can make yourself
comfortable with DebOps. Here is an example::

  [all_servers]
  serverone   ansible_ssh_host=serverone.example.com


**Verify you can access the server**

::

   $ ssh serverone.example.com
   $ debops-task all -m setup



.. WARNING::
   Ansible does not detect all platforms as detailed as it is
   required. Thus for some platforms running debops without any
   configuration will bring your system into a bad state. Please check
   `Notes about specific platforms`_ for more information. Sorry!

Before running ``debops`` the first time, we suggest you set up a minimal
configuration. This will make you more comfortable with the results.
For the very first try, you can put this into
``ansible/inventory/host_vars/serverone/vars.yml``::

  # Set custom timezone on the server
  ntp_timezone: 'Europe/Paris'

  # Protect the SSH service by specifying list of hosts/networks which can
  # access it (by default access is allowed from anywhere, but firewall blocks
  # too many connection attempts in a short amout of time)
  sshd_host_allow: [ '192.168.178.0/24' ]

  # Specify a mail server to send all mail through (it needs to accept the
  # incoming messages from your host)
  postfix_relayhost: 'mail.intern.example.com'

  # Set a default admin e-mail address where all messages to root account will
  # be forwarded
  postfix_default_local_alias_recipients: [ 'admin@example.com' ]


**Run the DebOps playbooks**

::

   $ debops


What you get after this
-----------------------

* apt-repositories and auto-update
* Firewall and tcpwrapper set up
* local mail forwarded to your central mail-hub
* Time synchronization with `pool.debian.org`



Where to go from here
---------------------

You may now start adding systems into ``ansible/inventory/hosts`` as
you like. To make install some software just add the host into the
resp. group and add some configuration options.



Prepare a new host for using DebOps
-----------------------------------

To add another host to DebOps a few requirements have to be fulfilled:

* The SSH private key of the user running ``debops`` has to be `loaded
  into ssh-agent <https://wiki.debian.org/SSH#ssh-agent_and_ssh-add>`_
  and the corresponding environment variables have to point to the
  running ``ssh-agent`` process.

* The SSH host key of the new host has to be added to the
  ``~/.ssh/known_hosts`` file of the user running ``debops``.

* It should be possible to login with `root` into the new host.

**Run the DebOps boostrap**

::

   $ debops bootstrap -u root -k -l <hostname>

This will install ``python`` and ``sudo`` on the target host, create an
account of the user running ``debops``, install its SSH public key into
the ``~/.ssh/authorized_keys`` file and grant it full ``sudo``
permissions.



Examples
--------

Setting up Etherpad quickly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``ansible/inventory/hosts``::

    [debops_etherpad]
    serverone

* ``ansible/inventory/host_vars/serverone/etherpad.yml``::

    etherpad_title: 'Our Corporate Etherpad'
    etherpad_disable_ip_logging: True
    etherpad_admins: [ 'etherpad-admin' ]

After running ``debops -l serverone`` you can access the running
etherpad on ``pad.example.com`` (given the hostname resolve
correctly). DebOps automatically installed and configured ``nginx``,
``nodejs`` and ``mysql`` (resp. ``mariadb``) for you.


More Examples
~~~~~~~~~~~~~~~~

You can find more examples in the `DebOps examples repository
<https://github.com/debops/examples>`_. If you have a an example you
want to share, please submit a pull-request. I'd happily integrate it.



Notes about specific platforms
------------------------------

If you need additional configuration for a platform, we suggest
putting this into a ``group_vars``-file and put the affected systems
into a group within ``ansible/inventory/hosts``.

Debian
   nothing to consider
Ubuntu
   nothing to consider
Rapbian (Debian for Raspberry PI)
   Requires some setup::

     # Default administrator account
     ansible_ssh_user: 'pi'

     # Work around missing detection of Raspbian in Ansible
     apt_default_sources_lookup: 'raspbian'
     apt_default_mirrors_lookup: 'raspbian'


..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
