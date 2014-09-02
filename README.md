## DebOps Playbooks

This repository contains all playbooks used by [DebOps](http://debops.org/) project.

##### Useful links

  * [DebOps project page](https://github.com/debops/) on GitHub
  * [DebOps Galaxy page](https://galaxy.ansible.com/list#/users/6081) on Ansible Galaxy

### Installation

To use these playbooks you will need [Ansible](http://ansible.com/)
installed on a control host (called "Ansible Controller"). You can refer to
Ansible [installation instructions](http://docs.ansible.com/intro_installation.html)
to try installing it manually, or check your distribution package manager for
already prepared packages.

To use these playbooks with corresponding Ansible roles, you need to clone this
repository to your own host, then download all roles using `ansible-galaxy`
command. Commands to execute on UNIX-like systems:

    git clone https://github.com/debops/debops-playbooks debops-playbooks
    cd debops-playbooks
    ansible-galaxy -p playbooks/roles install -r galaxy/requirements.txt

This will download all roles required by the DebOps playbooks.

They will be installed to `debops-playbooks/playbooks/roles/`. You can of
course omit the `-p` argument and then the roles will be installed to the
`roles/` path relative to where you installed Ansible. Depending on how you
installed Ansible this may require `sudo` access.

If you are updating already installed roles, `ansible-galaxy` might require the
`--force` option to overwrite existing roles.

### Playbook usage

To use these playbooks, you will need to create or provide an [Ansible
Inventory](http://docs.ansible.com/intro_inventory.html). When it's ready, you
can run the whole playbook with commands:

    cd path/to/debops-playbooks
    ansible-playbook -i path/to/inventory playbooks/site.yml

You can provide all other arguments to `ansible-playbook` if you want (for
example you can use `--tags` option to select specific roles, or `--limit`
option to select the host the playbook should interact with).

### Authors

DebOps Playbooks are written and maintained by the [DebOps](http://debops.org/)
developers. For specific author information refer to git commit logs.

