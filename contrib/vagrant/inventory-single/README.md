### vagrant-single - one server setup

This inventory will let you configure one VirtualBox virtual machine using
Vagrant and install selected application using Ansible. Currently available
applications:

- **GitLab CE** (default)
- **ownCloud**
- **phpIPAM**

You can select which application should be installed by editing
`inventory/hosts` file and commenting out specific host group.

To create the server, run `vagrant up` command. Vagrant should start
provisioning new host automatically.

After installation, point your browser to
[https://192.168.50.2/](https://192.168.50.2) to see the installed application.

