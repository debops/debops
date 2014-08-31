## debops.encfs
[![Platforms](http://img.shields.io/badge/platforms-debian%20|%20genericlinux%20|%20ubuntu-lightgrey.svg)](#)
### Warning, this is a BETA role

This role has been marked by the author as a beta role, which means that it
might be significantly changed in the future. Be careful while using this role
in a production environment.

***

Ansible role `encfs` allows you to create and manage directories using
[EncFS](https://en.wikipedia.org/wiki/EncFS), FUSE-based encrypted virtual
filesystem.

Primary mode of operation is to provide encrypted and secure storage space
for passwords and sensitive files on localhost (Ansible Controller) using
GPG-encrypted keyfile as password for EncFS. Access to 'root' account (via
sudo) is only required during a setup phase to install 'fuse' and 'encfs'
packages, and fix `/dev/fuse` access permissions; otherwise role works with
a regular user account.

Role supports directories in remote hosts encrypted using a password with
optional "passfile" as a transport for passwords in transit.



### Installation

To install `debops.encfs` using Ansible Galaxy, run:

    ansible-galaxy install debops.encfs


### Role variables

List of default variables available in the inventory:

    ---
    
    # Absolute path to a directory where encrypted filesystem will be mounted
    # Required
    encfs: False
    
    # Suffix of the directory with encrypted filesystem, it will be created in the
    # same path as the mount directory
    encfs_suffix: ".encrypted"
    
    # List of GPG keys to use to encrypt encfs keyfile. GPG encryption is supported
    # only on localhost (hosts which have ansible_connection=local set). Without
    # list of GPG recipients, GnuPG will ask for a passphrase instead
    encfs_gpg: []
    
    # Password to use instead of GPG keys / GPG passphrase. Supports encfs on
    # remote hosts. Will be sent via stdout and visible in 'ps' and Ansible logs,
    # use an external file with encfs_passfile to mitigate that.
    # You can populate this variable from an external file using lookup('file','path')
    encfs_password: False
    
    # An absolute path to file on remote host to store the password in transit.
    # Will be shredded when no longer needed. encfs role creates two files with this
    # name + suffixes '_init' and '_pass'
    encfs_passfile: False
    
    # By default encfs role behaves as a toggle - opens the encrypted filesystem if
    # it's closed, closes it if opened. By setting encfs_mode (for example with
    # --extra-vars) you can force desired mode of operation:
    #  - 'open' - create or open encrypted filesystem
    #  - 'close' - close encrypted filesystem
    encfs_mode: False
    
    # Device to use as source of randomness. You can change that to '/dev/urandom'
    # to use faster but weaker randomness source
    encfs_random: '/dev/random'



List of internal variables used by the role:

    encfs_user


### Detailed usage guide

To use 'encfs' role for encrypted storage for all your hosts, you should
set at least one variable (for example `secret`) in
`inventory/group_vars/all.yml` which will point to a directory in your
local filesystem. By default, 'encfs' will create an keyfile and encrypt it
using a GPG passphrase. To change how 'encfs' behaves, in
`inventory/host_vars/localhost.yml` set variables like `encfs_gpg`,
`encfs_password`, `encfs_passfile` (described above). This way the scope of
the `encfs_*` variables will be limited only to `localhost`.

You have to add 'localhost' to your inventory, preferably at the begginning
of the `hosts` file, like this:

    localhost ansible_connection=local

Add two plays at the beginning and end of your playbook, like this:

    ---
    - hosts: localhost
      sudo: no
      roles:
        - role: debops.encfs
          encfs: '{{ secret }}'
          encfs_mode: 'open'
    
    - hosts: all:!localhost
      # your plays here
    
    - hosts: localhost
      sudo: no
      roles:
        - role: debops.encfs
          encfs: '{{ secret }}'
          encfs_mode: 'close'

When you will run a playbook modified as above for the first time, Ansible
might require `sudo` access to install 'fuse' and 'encfs' packages, fix
`/dev/fuse` access permissions and add your user to 'fuse' group. If that
happens, 'encfs' role will stop playbook and inform you that you need to
log out and back in to have 'fuse' group available.

Another way to use 'encfs' role for encrypted global storage is to create
a shell script, and run that role using separate `ansible-playbook`
commands. Here's an example script:

    #!/bin/bash
    
    if [ $SECRET -gt 0 ] ; then
    	ansible-playbook -i inventory playbooks/secret.yml --extra-vars='encfs_mode=open'
    	trap "ansible-playbook -i inventory playbooks/secret.yml --extra-vars='encfs_mode=close'" EXIT
    fi
    
    ansible-playbook -i inventory playbooks/site.yml $@

And in `playbooks/secret.yml` you should create a playbook:

    - hosts: localhost
      sudo: no
      roles:
        - role: debops.encfs
          encfs: '{{ secret }}'

When you run that script, you can specify `ansible-playbook` options as
normal, and they will be used with correct command. When last of your plays
finishes, shell script will run Ansible with `encfs` role again, to close
encrypted filesystem.


### Authors and license

`debops.encfs` role was written by:

- Maciej Delmanowski - [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)


License: [GNU General Public License v3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))


***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).

