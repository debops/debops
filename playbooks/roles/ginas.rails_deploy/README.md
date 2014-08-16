### What does rails_deploy do?

It allows you to easily setup infrastructure capable of running rails applications. It removes all of the headaches associated to setting up a secure rails app that is ready for production so you can concentrate on developing your app.

### Getting started

Below is the bare minimum to get started. In this case everything would be on 1 host. There is a more robust example in [docs/examples/ansible](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible) where we setup the database on a different host and use postgres 9.3 instead of 9.1.

The full example includes setting up 3 containers with ginas:

- An app host
- A database host
- A local apt cache server to provide the app host a Ruby 2.1.x backport

This allows you to replicate a production environment locally so you can get
an idea of how your infrastructure will react in a real production environment.

#### hosts

```
[ginas_rails_yourappname]
somehost
```

#### inventory/host_vars/somehost.yml

`rails_deploy_git_location: 'git@github.com:youraccount/yourappname.git'`

The idea is you'll push your code somewhere and then the role will pull in from that repo.

#### playbook

```
---
- name: Deploy yourappname
  hosts: ginas_rails_yourappname
  sudo: true

  roles:
    - { role: ginas.rails_deploy, tags: yourappname }
```

#### Running the playbook

`ansible-playbook yourappname.yml -i /path/to/your/inv`

Check out the available tags in the [playbook example](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible/playbook/yourappname.yml).

### What are a few features available in this role?

- Setup an entire rails app server with 1 line of configuration with sane defaults
- Switch between postgresql and mysql with 1 line of configuration
- Postgresql runs a daily backup with daily/weekly rotation
- Switch between unicorn and puma with 1 line of configuration
  - Unicorn and puma configs are provided in [docs/examples/rails/config](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/rails/config)
- Optionally enable background worker support (sidekiq at the moment)
- Support syslog for rails itself, check the [rails requirements](#rails-requirements) for an example.
- Log your backend and worker to a logrotated file
- Easily separate your app and database servers when required
- Set users, permissions, services, run state and log paths automatically
- Set secure database passwords, generate ssh key pairs and ssl certs automatically
- Automatically set deploy keys to github/gitlab with 1 line of configuration
- Determine whether or not migrations need to happen by tracking paths in local facts
- Only run database oriented commands from a single master app server
- Intelligently attempt to reload or restart your server based on what changed
- Opt out of automatically migrating or opt in to always restart your server
- Manage external services at various points in the deploy cycle
- Manage custom tasks at various points in the deploy cycle
- Configure nginx as much as you need if the defaults aren't enough for you
- Show a temporary static deploy page during deploys with an automated cleanup of it afterwards
- Enable ssl by default and set it all for you automatically
- Protect everything behind a firewall that can be easily customized
  - If you have multiple hosts and separate database servers then it's up to you to configure it
  - An example of doing this is provided in [docs/examples/ansible/inventory](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible/inventory)
- Set as many environment vars as your app needs while also supplying many defaults
- Allow you to tweak about 50 heavily commented variables in [defaults/main.yml](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/defaults/main.yml)
- ...and more

### The defaults at a glance

- Postgresql
- Nginx
- Unicorn
- Sidekiq (if you enable the background worker, it's off by default)

You can find a few common usage examples at the bottom of the [defaults/main.yml](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/defaults/main.yml) file. You will see how to make changes to the defaults with very little configuration.

### Rails requirements

Make sure you have the unicorn/puma and postgres/mysql gems in your Gemfile. You will also want to use the example unicorn and puma configs in your app.

If you are using a background worker you'll want sidekiq in your Gemfile and you
should take a look at the example sidekiq configs.

You'll also want to use the `DATABASE_URL` format in your database.yml file. You can omit the production or whatever environment you're deploying to from the database.yml file and rails will pickup that env var by default.

If you want to use syslog for rails then you'll want to make sure you have this
in one of your environment configuration files:

```
require 'syslog/logger'

# ...

# The tags are optional but it's useful to have.
config.log_tags = [ :subdomain, :uuid ]

# This allows you to write to syslog::user without any additional gems/config.
config.logger = ActiveSupport::TaggedLogging.new(Syslog::Logger.new('yourappname'))
```

Lastly you should have 404, 422, 500 and 502 html files in your public directory. Nginx will serve them directly when those pesky errors decide to show up. You can also add a deploy.hml file in your public directory if you want to show a temporary maintenance/deploy page while your server is mid-deploy. If no deploy.html is found then this functionality will get skipped automatically.

### This role's requirements

It is expected you are deploying to Debian Wheezy with ginas. Wheezy's version of Ruby is quite old. To fix that ginas has a Ruby role which installs a non-managed version of Ruby to replace the old version.

This will give you the latest 2.1.x version of Ruby but rather than compile it from scratch every time you deploy a new app server it is expected that you setup a local apt cache host.

All of the hard work is done in the Ruby role but it does require you to configure ginas to provision the apt cache server and build ruby once.

You can simply use a container on your workstation to host it or throw it up on a $5/month digital ocean instance. It doesn't matter other than it must exist somewhere and is available when you install Ruby on your app server.

The [inventory example](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible/inventory) contains information on how to set this up using a container. It's very little configuration, it just takes about 10-15 minutes to setup once while ansible provisions the server. After that your app servers will be able to install Ruby in about 10 seconds.

Once Debian Jessie is feature frozen (~November 2014) then this step will be removed because Jessie will use Ruby 2.1.x by default.

#### Commands to run once your inventory is ready

```
# cd to your ginas directory

./site.sh -l ansible_controller -t lxc
# ssh into each container to accept the initial ssh connection warning.
./site.sh -l containers
# Uncomment line 6 in inventory/group_vars/containers.yml.
./site.sh -l containers -t apt
./site.sh -l ginas_postgresql # Only if you're using multiple hosts.
# You are done. At this point you can run the playbook to setup your app server.
```

### FAQ / troubleshooting guide

##### You switched from unicorn to puma or puma to unicorn and the site is dead
Chances are you're deploying with tags so the entire role did not run. When you switch servers nginx needs to be restarted. Make sure you `-t nginx` or just run the whole role when you change servers.

##### You can't clone your repo
Since the role needs to pull in from your git repo then it needs permission to your repo. The most common way to do that is to setup an API access token for github.

Gitlab is also supported, all of this is documented in the [defaults/main.yml](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/defaults/main.yml) file.

##### How would you go about setting up a CI platform with this role?
Rather than impose a CI solution on you, you're free to do whatever you want.

A possible situation might be to use this role to deploy to a staging/CI/build server instead of directly to production. Now your build server can run tests and push to production using this role on different hosts if everything goes well.

That would allow you to have a sweet CI setup where your developers only have to git push somewhere and minutes later you have tested code in production if you don't have to worry about a ton of red tape.

### License

[GPLv3](https://www.gnu.org/licenses/quick-guide-gplv3.html)

### Author

`ginas.rails_deploy` was created by Nick Janetakis nick.janetakis@gmail.com.
