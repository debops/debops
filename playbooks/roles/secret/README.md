# secret

Ansible role `secret` allows you to store and update passwords, certificates and other sensitive data in a secure way. To achieve this, `secret` uses `cryptsetup` command and LUKS to create encrypted storage file with configurable size, protected by a keyfile encrypted with GnuPG, either using symmetric encryption with a passphrase, or OpenPGP public key encryption with one or multiple GPG keys.

## Big Scary Warning

- this role uses `root` account on your local machine using `sudo` and running commands like `dd`, `mkfs.ext2` and `cryptsetup luksFormat`. If you want to use it, read this file carefully.

- this role was developed and is used on Ubuntu Linux, and works with Ubuntu or Debian. It might not work on your machine. It might not work on your distribution. It might delete all your data. You have been warned.

## How to use it

First, add `localhost` to list of hosts in inventory, preferably at the beginning and not inside any of the host groups. [ginas](https://github.com/drybjed/ginas/) has been prepared to deal with this correctly, if you want to try it in your own playbook, make sure that you use `- hosts: all:!localhost` in your playbook definition to ignore `localhost` while running other plays.

Put variables listed below in inventory. The best place would be in `group_vars/all.yml` to have one global secret storage. Using separate variables for different host groups haven't been tested and is currently not supported.

- `secret`: **absolute path to a directory in your local filesystem**. It has to exist, and your user should have access rights. It will be used as a mount point for encrypted storage while it is opened, so use empty directory and avoid putting it in place that might change during playbook execution. Mandatory.

- `secret_gpg`: list of one or more OpenPGP public keys to use for encryption. If this variable is not defined in inventory, GnuPG will ask for a passphrase during storage creation and every time encrypted storage is opened; with OpenPGP keys GnuPG can utilize `gpg-agent` for decryption (has to be configured in `~/.gnupg/gpg.conf`). Optional.

- `secret_size`: size of encrypted storage in MB. By default, 64 MB. Optional.

- `secret_random`: device that will be used to get randomness from, `/dev/random` by default. You might want to switch it to `/dev/urandom` on development/testing hosts to speed up certain operations. Optional.

Now you can add two plays at the beginning and end of your playbook, like this:
```
---
- hosts: localhost
  sudo: no
  roles:
    - { role: secret, secret_mode: 'open' }

- hosts: all:!localhost
  # your plays here

- hosts: localhost
  sudo: no
  roles:
    - { role: secret }
```
This way, Ansible will use `secret` role to create and/or open secret storage, run your playbooks and close secret storage at the end (during execution, files inside secret storage will be mounted in place of `secret` directory with owner and group of your user and `0700` permissions). This method has a disadvantage - when you use `ansible-playbook` command, you need to specify `--limit group,localhost` each time, or `secret` role will not be executed by Ansible.

Another way to use `secret` role is to create a shell script, and run that role using separate `ansible-playbook` command. Here's an example script used in [ginas](https://github.com/drybjed/ginas/):
```
#!/bin/sh

if [ -z "${TOO_MANY_SECRETS}" ] ; then
	ansible-playbook -i inventory playbooks/secret.yml --extra-vars="secret_mode=open"
	trap "ansible-playbook -i inventory playbooks/secret.yml" EXIT
fi

ansible-playbook -i inventory playbooks/site.yml $@
```
And in `playbooks/secret.yml` you should create a playbook:
```
- hosts: localhost
  sudo: no
  roles:
    - { role: secret }
```
When you run that script, you can specify `ansible-playbook` options as normal, and they will be used in correct command. When last of your plays finishes, shell script will run Ansible with `secret` role again, to close secret storage.

## Problems and tips

- `secret` role uses `sudo` directly for some commands, without using `sudo: yes` in Ansible playbook. I tried to use "proper" way, but couldn't make Ansible work properly with combination of `gpg-agent` and `sudo`. With default configuration on Ubuntu, after `sudo` asks for a password the first time, it remembers access rights for subsequent invocations for short period of time, so that helps a bit.

- sometimes Ansible stops while trying to decrypt storage with combination of GnuPG asking for key passphrase and `sudo` asking for user password. Interrupting Ansible using `Ctrl+C` and starting playbook again seems to help.

- if you want to run Ansible with `secret` role without Xorg (in a console for example), Ansible will fail while GnuPG is asking for a key passphrase. Solution is to use `gpg-agent` and provide it with a password before running a playbook.

