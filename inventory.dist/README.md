## Example inventory directory for Ansible

This is an example inventory directory. To use it, rename it to 'inventory' and fill with your own variables. Git will ignore the 'inventory' directory (it's set in .gitignore). After that you can run Ansible with:

    ansible-playbook -i inventory site.yml

To use a specific staging or production hosts file, run Ansible using:

    ansible-playbook -i inventory/staging site.yml
    ansible-playbook -i inventory/production site.yml

If you want, you can set the inventory directory as default in `ansible.cfg`:

    [defaults]
    hostfile = inventory

That way, Ansible will look for 'inventory/hosts' file relative to current directory.

