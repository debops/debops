What does this guide cover?
---------------------------

The general theme of this guide will be how to install ansible on your
work station and then use ginas to manage 0 or more linux containers so
you can happily setup and teardown servers that mimic your production
environment!

What operating systems are compatible as work stations?
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

This guide was written and tested against a fresh xubuntu 14.04 work
station however similar ubuntu derivatives should work.

What operating systems are compatible as containers?
''''''''''''''''''''''''''''''''''''''''''''''''''''

By default ginas will use debian wheezy as the base for each container
it creates. For the most part it is compatible with ubuntu 12.04 LTS.
You may have to make a few minor changes in your custom playbooks to
make it work on both debian wheezy and ubuntu 12.04 LTS.

What is the ansible skill level expectation for this guide?
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

You are expected to be pretty familiar with ansible but you definitely
do not need to be an expert. You should know what an inventory or
playbook is, etc..

Table of contents
-----------------

-  `Install ansible on your work station <#install-ansible>`__
-  `Configure your inventory <#configure-inventory>`__
-  `Run the common playbook <#common-playbook>`__
-  `Setup your first linux container <#first-container>`__
-  `Access your container in a browser from your work station <#browse-container>`__

Install ansible on your work station
------------------------------------

For the sake of this guide we are going to make a few assumptions about
where things will be installed and what the hostname of the work station
is. Feel free to customize these values because they are not important
to getting ansible and ginas setup correctly.

The work station will be named ``beast`` and your "I put my source code
here" path will be ``~/src``.

::

    # -----------------------------------------------------------------------------
    # Install the bare necessities.
    # -----------------------------------------------------------------------------
    # TIP: Feel free to remove vim and mc (midnight commander) if you don't want em.
    sudo apt-get install git lsb-release vim mc make

    # -----------------------------------------------------------------------------
    # Clone ginas into a directory of your choice.
    # -----------------------------------------------------------------------------
    # TIP: For the sake of this guide we are cloning to ~/src/ansible.
    git clone https://github.com/ginas/ginas.git ~/src/ansible/ginas

    # -----------------------------------------------------------------------------
    # Setup the inventory file and directories.
    # -----------------------------------------------------------------------------
    cd ~/src/ansible/ginas
    mkdir -p hosts inventory/group_vars inventory_host_vars

    # -----------------------------------------------------------------------------
    # Run the bootstrap command to install ansible.
    # -----------------------------------------------------------------------------
    # TIP: It will install the development branch which is reasonably stable.
    ./contrib/bootstrap-ansible.sh

At this point you should have ansible installed on your work station.
You can verify this by entering ``ansible --version`` in your terminal.
You should get back a version number.

Configure your inventory
------------------------

Now for the good stuff, we're going to run the common tasks for ginas.
First off we will configure some basic settings though.

::

    # -----------------------------------------------------------------------------
    # Add any custom packages you want installed.
    # -----------------------------------------------------------------------------
    vi inventory/host_vars/beast.yml

    # Your file could look like this (without the comments):
    ---
      # Install libpq-dev because I am a rails developer and I want to be able to connect
      # to a postgres database. You do not need this unless you have the same needs as me.
      apt_host_packages: ['libpq-dev']

      # Notice how it's added to the apt_host_packages list. This will only be applied to
      # your work station which is named beast.

    # -----------------------------------------------------------------------------
    # Setup basic configuration to be applied to all hosts.
    # -----------------------------------------------------------------------------
    vi inventory/group_vars/all.yml

    # Your file should look like this (without the comments):
    ---
      # Remove this line if you do not want dotfiles installed.
      users_dotfiles_enabled_default: True

      # Remove this line if you want bash instead.
      users_default_shell: '/bin/zsh'

      # The admin account of the server will be set as ansible_ssh_user.
      # If you run your playbook without setting -u <some user> then
      # ansible will use your work station's user as the default.
      auth_admin_accounts: [ '{{ ansible_ssh_user }}' ]

      # Some configuration to ensure packages are pulled from the correct mirror.
      # TIP: If you are not from the US you might want to change the mirror url.
      apt_debian_http_mirror: 'ftp.us.debian.org'
      lxc_template_debootstrap_mirror: 'http://{{ apt_debian_http_mirror }}/debian'

      # Set the default locale.
      # TIP: If you are not from the US you might want to use a different locale.
      console_locales: ['en_US.UTF-8']

    # -----------------------------------------------------------------------------
    # Setup the hosts file
    # -----------------------------------------------------------------------------
    vi hosts

    # Your file should look like this (without the comments):
    ---
      # This tells ansible that you want commands to be ran locally for localhost.
      localhost ansible_connection=local

      # We are grouping our work station to limit tasks later for only our WS.
      [ansible_workstation]
      beast ansible_connection=local

If all goes as planned you should be able to check out some ansible
facts about your host by entering ``./task.sh beast -m setup | less``.
If that command worked you should see the facts and that verifies
ansible has been setup correctly and is capable of talking to your work
station.

Run the common playbook
-----------------------

Now that everything is configured we can run the common playbook. This
is going to setup your work station with proper DNS, postfix support and
many other useful services. This section is short and sweet. Just enter
``./site.sh -K`` and provide your sudo password. In the future we won't
have to provide -K because one of the things that the common playbook
does is setup ssh keys and enable passwordless sudo.

If that worked properly then you must log out of your work station and
log back in. Certain permissions were changed for your user so that step
is required, you cannot just open a new terminal or source your shell
config.

After logging back in you should verify that you can access root without
a password. Enter ``sudo su`` and you should be greeted with a root
prompt. Just hit ``CTRL+D`` or type ``logout`` to get back to your
normal user.

Setup your first linux container
--------------------------------

This is where things get interesting. In a few minutes you'll be able to
setup as many linux containers as you want in seconds.

::

    # -----------------------------------------------------------------------------
    # Make sure your ssh keys are setup
    # -----------------------------------------------------------------------------
    # TIP: Skip this step and copy over any existing keys to ~/.ssh if you have em.
    ssh-keygein -t rsa

    # -----------------------------------------------------------------------------
    # Fix a potential bug with ubuntu and linux containers
    # -----------------------------------------------------------------------------
    # You will likely get errors without installing this package first.
    sudo apt-get install libcgmanager0

    # -----------------------------------------------------------------------------
    # Create the container in your inventory
    # -----------------------------------------------------------------------------
    # TIP: Add the following to this file.
    vi inventory/host_vars/beast.yml

    # A list of containers to add.
    lxc_containers:
        # What should the container be named?
      - name: 'first'
        # Should it be started automatically?
        # TIP: You can set this to 'absent' to delete the container.
        state: 'started'
        # Setup nat.
        network: 'nat'
        config: True

    # -----------------------------------------------------------------------------
    # Add the container to your hosts
    # -----------------------------------------------------------------------------
    # TIP: Add the following to this file.
    vi inventory/hosts

    # We want to let ginas know that our work station will be storing the containers.
    [ginas_lxc]
    beast

    # -----------------------------------------------------------------------------
    # Create the container
    # -----------------------------------------------------------------------------
    # Run the lxc role on the work station.
    ./site.sh --limit ginas_lxc

    # You can expect this command to take a while on the first run. The first
    # container has to download a bunch of packages from apt but once it finishes
    # the first run it caches those packages.

    # Future containers will take only a few seconds to create even if you delete
    # this one. Yep, linux containers are amazing.

You should now have a container available to be managed by whatever you
want. You can verify that it works by typing:

``ping first`` and ``ssh first``. Since we have DNS setup properly we
can access them easily.

To add more containers just open ``inventory/host_vars/beast.yml`` and
add it to the list of containers. Then run ``./site.sh --tags lxc`` and
it will be added.

You can also see which containers are running by entering
``sudo lxc-ls -f``. Another tip to delete containers faster is to enter
``sudo lxc-destroy -f -n <container_name>`` rather than changing the
inventory to set it as absent.

Access your container in a browser from your work station
---------------------------------------------------------

All of the commands below are to be ran on your work station.

::

    # -----------------------------------------------------------------------------
    # Let /etc/hosts know about your work station domain
    # -----------------------------------------------------------------------------
    sudo vi /etc/hosts

    # Edit your file to include this line by ovewriting the old 127.0.1.1 line.
    # TIP: You can choose something other than .dev, but you need at least 1 dot.
    127.0.1.1   beast.dev beast

    # -----------------------------------------------------------------------------
    # Enable wildcard sub-domain support
    # -----------------------------------------------------------------------------
    vi inventory/host_vars/beast.yml

    # You must add each container to this list.
    dnsmasq_address:
      # first... this is the container name.
      # nat...   we are on the network.
      # beast... your work station hostname.
      # dev...   the extension
      # IP...    this is the IP address of the container
      '.first.nat.beast.dev': '192.168.144.1'

      # TIP: To find the IP address of the container run this:
      # cat /etc/network/interfaces.d/40_nat_br2
      # It will be marked next to the 'address' field.

    # -----------------------------------------------------------------------------
    # Update your containers to reflect the DNS changes
    # -----------------------------------------------------------------------------
    ./site --limit ginas_lxc

You can verify that wildcard sub-domains work by entering
``ping foo.first``, you should get a reply.

That's it. You can now open a browser on your work station and visit
``http://first.nat.beast.dev/``. You will get an unable to connect
message because there are no web servers running. You can verify this by
trying to goto ``http://foo.nat.beast.dev``, you will see a no server
errror instead.

Have fun
''''''''

Don't forget to use ansible to provision your containers!
