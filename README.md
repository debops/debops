## rails_deploy

[![Travis CI](https://secure.travis-ci.org/debops/ansible-rails_deploy.png)](http://travis-ci.org/debops/ansible-rails_deploy) [![test-suite](http://img.shields.io/badge/test--suite-ansible--rails__deploy-blue.svg)](https://github.com/debops/test-suite/tree/master/ansible-rails_deploy/) [![Ansible Galaxy](http://img.shields.io/badge/galaxy-debops.rails__deploy-660198.svg)](https://galaxy.ansible.com/list#/roles/1591)[![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg)](#)

`debops.rails_deploy` role allows you to easily setup infrastructure
capable of running Rails applications. It removes all of the headaches
associated to setting up a secure Rails app that is ready for production so
you can concentrate on developing your app.


### Installation

This role requires at least Ansible `v1.7.0`. To install it, run:

    ansible-galaxy install debops.rails_deploy



### Role dependencies

- `debops.secret`
- `debops.etc_services`
- `debops.nodejs`
- `debops.ruby`
- `debops.redis`
- `debops.postgresql`
- `debops.mysql`
- `debops.nginx`
- `debops.monit`
- `debops.monit`



### Role variables

List of default variables available in the inventory:

    ---
    
    # ---- System ----
    
    # Should postgresql or mysql and nginx be setup for you automatically?
    # Redis will also be setup if you enable background worker support.
    # Critical dependencies like nodejs and ruby will always be setup for you.
    # If you want anything to be on a non-app host then you would remove it here.
    rails_deploy_dependencies: ['database', 'redis', 'nginx']
    
    # Which packages do you want installed?
    # Add as many packages as you want, the database_package will automatically
    # pick libpq-dev or libmysqlclient-dev depending on what database you picked.
    rails_deploy_packages: ['{{ rails_deploy_database_package }}']
    
    # A list of additional groups that this app's user belongs to.
    # If you want to be able to ssh into the server then you must include 'sshusers'.
    rails_deploy_user_groups: []
    
    # Where should the public ssh key be read in from? This is only used when you
    # have included 'sshusers' in the user_groups list.
    rails_deploy_user_sshkey: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
    
    
    # ---- Hosts ----
    
    # What inventory group does your app belong to?
    rails_deploy_hosts_group: 'debops_rails_{{ rails_deploy_service }}'
    
    # Which application server should run database related tasks?
    rails_deploy_hosts_master: '{{ groups[rails_deploy_hosts_group][0] }}'
    
    
    # ---- Git ----
    
    # The location repo which will get cloned during each deploy. You can use a
    # remote or local repo.
    rails_deploy_git_location: ''
    
    # Which branch or tag should be used?
    rails_deploy_git_version: 'master'
    
    # Which remote should be used?
    rails_deploy_git_remote: 'origin'
    
    # Supply your git provider's api token to automatically set deploy keys.
    # If False you will have to manually add deploy keys for each app server.
    
    # Supports github and gitlab for now:
    # Github: https://github.com/settings/applications
    #   Under personal access tokens, check off 'write:public_key'.
    #     You may want to enable other access limits for repo/public_repo, etc..
    #
    # Gitlab: https://yourgitlabhost.com/profile/account
    #   Your private token should already be there.
    rails_deploy_git_access_token: False
    
    
    # ---- Deploy ----
    
    # What should the service be named?
    # The default value plucks out your repo name (without .git) from your location.
    rails_deploy_service: "{{ rails_deploy_git_location | basename | replace('.git', '') }}"
    
    # What should the system environment be set to?
    rails_deploy_system_env: 'production'
    
    # A list of environments to skip, it will remove your system env from the list
    # during the deploy phase automatically.
    rails_deploy_bundle_without: ['development', 'staging', 'production', 'test']
    
    
    # ---- Backend ----
    
    # Which backend type are you using? 'unicorn' and 'puma' are supported so far.
    rails_deploy_backend: 'unicorn'
    
    # What do you want to listen on? You can choose a tcp addr:port or unix socket.
    # Do not bother to include the socket/tcp prefix, that will be handled for you.
    rails_deploy_backend_bind: '{{ rails_deploy_service_socket }}'
    
    # What state should the backend be in?
    rails_deploy_backend_state: 'started'
    rails_deploy_backend_enabled: True
    
    # When set to true the backend will always restart instead of reload but it
    # will only restart if the repo changed. This makes for hands free deployment
    # at the cost of a few seconds+ of downtime per deploy.
    #
    # You may want to combine this with force migrate in which case all you ever have
    # to do is push your app and you don't have to wonder whether or not the code
    # you're changing requires a full restart or not.
    rails_deploy_backend_always_restart: False
    
    
    # ---- Database ----
    
    # Should the database be created by default?
    rails_deploy_database_create: True
    
    # Should the database get a db:schema:load and db:seed in an idempotent way?
    rails_deploy_database_prepare: True
    
    # Should the database get automatically migrated in an idempotent way?
    rails_deploy_database_migrate: True
    
    # Should the database get migrated no matter what?
    # You may want to do this as a 1 off command with --extra-vars in case your
    # schema file's checksum somehow gets out of sync and you need to migrate.
    #
    # Another use case would be if you have automatic migrations turned off and
    # you just deployed but now you want to do an isolated migration.
    rails_deploy_database_force_migrate: False
    
    # It supports 'postgresql' or 'mysql' for now.
    rails_deploy_database_adapter: 'postgresql'
    
    # Make sure this matches your pg cluster info, ignore it if you use mysql.
    rails_deploy_postgresql_cluster: '9.1/main'
    
    # Where is your database hosted?
    rails_deploy_database_host: '{{ ansible_fqdn }}'
    rails_deploy_database_port: '5432' # 3306 for mysql
    
    # What are your super user names?
    rails_deploy_postgresql_super_username: 'postgres'
    rails_deploy_mysql_super_username: 'mysql'
    
    # What should some of the configuration options be set to?
    rails_deploy_database_pool: 25
    rails_deploy_database_timeout: 5000
    
    
    # ---- Background Worker ----
    
    # Enable background worker support. This will create an init.d service, register
    # it with monit and add it into the deploy life cycle.
    rails_deploy_worker_enabled: False
    rails_deploy_worker_state: 'started'
    
    # At the moment it only supports sidekiq but resque could happen in the future.
    rails_deploy_worker: 'sidekiq'
    
    # Where is your worker hosted?
    rails_deploy_worker_host: '{{ ansible_fqdn }}'
    rails_deploy_worker_port: '6379'
    
    # How should the connection be made to the redis server?
    # If your server has a password you must add it here.
    # Example: redis://:mypassword@{{ rails_deploy_worker_host }}:{{ rails_deploy_worker_port }}/0'
    rails_deploy_worker_url: 'redis://{{ rails_deploy_worker_host }}:{{ rails_deploy_worker_port }}/0'
    
    
    # ---- Tasks ----
    
    # Precompile assets and remove any temporary cache files on each deploy.
    # Add or remove as many tasks as you want. They are executed in the context
    # of the root directory of your app and only happen when the repo changes.
    rails_deploy_default_tasks:
      - 'bundle exec rake assets:precompile'
      - 'rm -rf tmp/cache'
    
    # Execute tasks before and/or after your backend is reloaded/restarted.
    rails_deploy_early_tasks:
      # Example, let's say you wanted to execute whenever also:
      # - 'bundle exec whenever --clear-crontab {{ rails_deploy_service }}'
    
    # This is the absolute last thing that happens during a deploy.
    rails_deploy_late_tasks: []
    
    
    # ---- Services ----
    
    # Add 1 or more custom services related to the app, they will have
    # their state changed on each deploy. The changed_state is the action to
    # take when the state of the git repo has changed.
    
    # They will get restarted/reloaded at the end of the deploy.
    # Everything is optional except for the name.
    rails_deploy_extra_services: []
    
    #rails_deploy_extra_services:
    #  - name: ''
    #    changed_state: 'reloaded'
    #    state: 'started'
    #    enabled: True
    
    
    # ---- Log rotation ----
    
    # How often should they be rotated?
    # Accepted values: hourly, daily, weekly, monthly and yearly
    rails_deploy_logrotate_interval: 'weekly'
    
    # Log files are rotated N times before being removed.
    rails_deploy_logrotate_rotation: 24
    
    
    # ---- Environment settings ----
    
    # Both the default and custom environment variables will get added together
    # and be written to /etc/default/{{ rails_deploy_service }}.
    
    # Default environment variables added to each app.
    rails_deploy_default_env:
      RAILS_ENV: '{{ rails_deploy_system_env }}'
    
      DATABASE_URL: "{{ rails_deploy_database_adapter }}://{{ rails_deploy_service }}:{{ rails_deploy_database_user_password }}@{{ rails_deploy_database_host }}:{{ rails_deploy_database_port }}/{{ rails_deploy_service }}_{{ rails_deploy_system_env }}?pool={{ rails_deploy_database_pool }}&timeout={{ rails_deploy_database_timeout }}"
    
      # Application variables, they are used in the backend/worker variables below.
      SERVICE: '{{ rails_deploy_service }}'
      LOG_FILE: '{{ rails_deploy_log }}/{{ rails_deploy_service }}.log'
      RUN_STATE_PATH: '{{ rails_deploy_run }}'
    
      # Backend variables, they work in conjunction with the example
      # server configs. Check docs/examples/rails/config/puma.rb|unicorn.rb.
      LISTEN_ON: '{{ rails_deploy_backend_bind }}'
    
      THREADS_MIN: 0
      THREADS_MAX: 16
      WORKERS: 2
    
      # Background worker variables. Check docs/examples/rails/config/sidekiq.yml
      # and initializers/sidekiq.rb on how use this in your application.
      BACKGROUND_URL: '{{ rails_deploy_worker_url }}'
      BACKGROUND_THREADS: '{{ rails_deploy_database_pool }}'
    
    # Custom environment variables added to a specific app.
    rails_deploy_env: {}
    
    
    # ---- Nginx settings ----
    
    # Should nginx be enabled?
    rails_deploy_nginx_server_enabled: True
    
    # What domain names should the app be associated to?
    rails_deploy_nginx_domains: ['{{ ansible_fqdn }}']
    
    # If you want to edit any of the values for nginx below, you will need to copy
    # the whole variable over even if you need to edit 1 value.
    #
    # Consult the debops.nginx documentation if needed.
    
    # Configure the upstream.
    rails_deploy_nginx_upstream:
      enabled: '{{ rails_deploy_nginx_server_enabled }}'
      name: '{{ rails_deploy_service }}'
      server: "{{ 'unix:' + rails_deploy_backend_bind if not ':' in rails_deploy_backend_bind else rails_deploy_backend_bind }}"
    
    # Configure the sites-available.
    rails_deploy_nginx_server:
      enabled: '{{ rails_deploy_nginx_server_enabled }}'
      default: False
      name: '{{ rails_deploy_nginx_domains }}'
      root: '{{ rails_deploy_src }}/public'
    
      error_pages:
        '404': '/404.html'
        '422': '/422.html'
        '500': '/500.html'
        '502 503 504': '/502.html'
    
      location_list:
        - pattern: '/'
          options: |
            try_files $uri $uri/index.html $uri.html @{{ rails_deploy_nginx_upstream.name }};
        - pattern: '~ ^/(assets|system)/'
          options: |
            gzip_static on;
            expires max;
            add_header Cache-Control public;
            add_header Last-Modified "";
            add_header ETag "";
        - pattern: '@{{ rails_deploy_nginx_upstream.name }}'
          options: |
            gzip off;
            proxy_set_header   X-Forwarded-Proto $scheme;
            proxy_set_header   Host              $http_host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_redirect     off;
            proxy_pass         http://{{ rails_deploy_nginx_upstream.name }};
    
    
    # Usage examples:
    
    # ---- Bare minimum ----
    #rails_deploy_git_location: 'git@github.com:yourname/mycoolapp.git'
    
    # ---- Use a custom service name ----
    #rails_deploy_service: 'myawesomeapp'
    
    # ---- Use a tag or branch instead of master ----
    #rails_deploy_git_version: 'v0.1.0'
    
    # ---- Use mysql instead of postgres ----
    #rails_deploy_database_adapter: 'mysql'
    
    # ---- Use puma instead of unicorn ----
    #rails_deploy_backend: 'puma'
    
    # ---- Enable the background worker ----
    #rails_deploy_worker_enable: True
    
    # ---- Listen on a tcp port instead of a socket ----
    #rails_deploy_backend_bind: '{{ ansible_fqdn }}:8080'
    
    # ---- Deploy to staging instead of production ----
    #rails_deploy_system_env: 'staging'



List of internal variables used by the role:

    rails_deploy_key_data


### Detailed usage guide

Below is the bare minimum to get started. In this case everything would be
on 1 host. There is a more robust example in
[docs/examples/ansible](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible)
where we setup the database on a different host and use postgres 9.3
instead of 9.1.

The full example includes setting up 3 containers with ginas:

- An app host
- A database host
- A local apt cache server to provide the app host a Ruby 2.1.x backport

This allows you to replicate a production environment locally so you can
get an idea of how your infrastructure will react in a real production
environment.

#### hosts

    [debops_rails_yourappname]
    somehost

#### inventory/host_vars/somehost.yml

    ---
    rails_deploy_git_location: 'git@github.com:youraccount/yourappname.git'

The idea is that you'll push your code somewhere and then the role will
pull in from that repo.

#### playbook

    ---
    - name: Deploy yourappname
      hosts: debops_rails_yourappname
      sudo: true
    
      roles:
        - { role: debops.rails_deploy, tags: yourappname }

#### Running the playbook

    ansible-playbook yourappname.yml -i /path/to/your/inventory

Check out the available tags in the [playbook
example](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible/playbook/yourappname.yml).

#### The defaults at a glance

- Postgresql (switching to MySQL is 1 line of yaml)
- Sidekiq (if you enable the background worker, it's off by default)
- `unicorn` (switching to `puma` is 1 line of yaml)
- `nginx`

You can find a few common usage examples at the bottom of the
[defaults/main.yml](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/defaults/main.yml)
file.

#### A few features supplied by this role

##### High level goals

- Setup an entire rails app server with 1 line of configuration with sane defaults
- Optionally and easily separate your app servers, database and worker into multiple servers
- Quickly and easily switch between popular default databases and backend servers
- Be as secure as possible and adhere to as many best practices as possible

##### Backups and logging

- Postgresql runs a daily backup with daily/weekly rotation
- Both your backend server and background worker get logged to 1 logrotated file
- The rails process gets sent to syslog.user

##### System level minutia

- User accounts, permissions and ssh keys are automatically managed
- Paths such as logs, pids and sockets are automatically managed

##### Deploy features
- Automatically set deploy keys to github/gitlab with 1 line of configuration
  - This leverages their API, all you have to do is supply their token
- Keep track of your schema file and config folder's mtime in local facts
  - This allows the deploy task to attempt to guess if your server needs a full restart or a quick reload
- Only run database commands from a single master app server
  - This master is defined by simply being first in the group list
- Various options to turn certain features on/off
  - A few examples would be database creation, migration and force restarting your server
- Add custom services which get restarted/reloaded at the end of the deploy cycle
  - If you have a SOA setup this could be handy
- Add and remove custom tasks
  - By default it is set to precompile assets and clear the /tmp cache
- Optionally swap a static deploy page in/out during the deploy cycle

##### Security
- Secure passwords are managed automatically for your database
- Ports are blocked and only whitelisted for IP addresses/masks that you specify
  - An example of this is supplied in the [inventory example](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible/inventory).
- SSL is enabled by default but can be turned off if you really don't want it
- Self signed SSL certs are automatically managed for you
  - Changing to properly signed certificates is a breeze

#### Changes you need to make in your rails application

##### Gemfile

You must have unicorn **or** puma added.
    # Pick one, you may also want to bump the version to the most recent version.
    # These are the most recent as of ~August 2014.
    gem 'unicorn', '~> 4.8.3'
    gem 'puma', '~> 2.9.0'

You must have pg **or** mysql2 added.
    # Pick one, you may also want to bump the version to the most recent version.
    # These are the most recent as of ~August 2014.
    gem 'pg', '~> 0.17.1'
    gem 'mysql2', '~> 0.3.16'

##### Backend server config

You should base your unicorn or puma config off our [example
configs](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/rails/config)
because certain environment variables are required to exist. Also certain
signals are sent to reload or restart the backend which require certain
configuration options to be set. Luckily you don't have to think about any
of that, just use the pre-written configs in your app.

##### Background worker config

You should also base your sidekiq configs off our [example
configs](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/rails/config).
Similar to the backend server it expects certain environment variables to
exist.

##### Database config

The database configuration below would be reasonable to use. The only
requirement is that yours must use the `DATABASE_URL` format in whatever
environments you plan to deploy to. That simply means that those
environments should be removed from your database config file. This role
sets up the `DATABASE_URL` for you.

    ---
    development:
      url: <%= ENV['DATABASE_URL'].gsub('?', '_development?') %>
    test:
      url: <%= ENV['DATABASE_URL'].gsub('?', '_test?') %>

##### Application config

In order to log everything to 1 file you must drop this line into your
application config. This would apply to all environments. Feel free to move
this to only staging and/or production if you don't want this to happen in
development.

    config.paths['log'] = ENV['LOG_FILE']

##### Production environment config

Chances are you'll want your rails app to write to syslog in production or
on your staging/build/etc. server. Copy this into your production
environment config.

    require 'syslog/logger'
    
    # ...
    
    # The tags are optional but it's useful to have.
    config.log_tags = [ :subdomain, :uuid ]
    
    # This allows you to write to syslog::user without any additional gems/config.
    config.logger = ActiveSupport::TaggedLogging.new(Syslog::Logger.new('yourappname'))

##### Public files

You will likely want the following files to exist in your `/public`
directory:

- 404, 422, 500 and 502 html files to process error pages
- deploy html file to swap in/out during the deploy process

The above will allow nginx to serve those files directly before rails even
gets a chance.

#### Don't feel like making these small changes every time you make a new app?

Me neither. That's why I created [orats](https://github.com/nickjj/orats).
It is a command line tool that generates a shiny new rails application with
an accumulation of best practices that I have picked up over time. It is
also a little opinionated. Check out [orats' git
repo](https://github.com/nickjj/orats) if you're interested.

#### This role's requirements

It is expected you are deploying to Debian Wheezy with
[DebOps](http://debops.org/). Wheezy's version of Ruby is quite old. To fix
that, DebOps has a Ruby role which installs a version of Ruby backported
from Debian Jessie.

This will give you the latest 2.1.x version of Ruby but rather than compile
it from scratch every time you deploy a new app server it is expected that
you setup a local apt cache host (this can be done using `debops.apt` role).

All of the hard work is done in the Ruby role but it does require you to
configure DebOps to provision the apt cache server and build ruby once.

You can simply use a container on your workstation to host it or throw it
up on a $5/month Digital Ocean instance. It doesn't matter other than it
must exist somewhere and is available when you install Ruby on your app
server.

The [inventory
example](https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.rails_deploy/docs/examples/ansible/inventory)
contains information on how to set this up using a container. It's very
little configuration, it just takes about 10-15 minutes to setup once while
Ansible provisions the server. After that your app servers will be able to
install Ruby in about 10 seconds.

Once Debian Jessie becomes Stable, Ruby 2.1 packages will be available by
default and backporting will be unnecessary.

#### Commands to run once your inventory is ready

    # cd to your ginas directory
    
    ./site.sh -l ansible_controller -t lxc
    # ssh into each container to accept the initial ssh connection warning.
    ./site.sh -l containers
    # Uncomment line 6 in inventory/group_vars/containers.yml.
    ./site.sh -l containers -t apt
    ./site.sh -l ginas_postgresql # Only if you're using multiple hosts.
    # You are done. At this point you can run the playbook to setup your app server.

#### FAQ / troubleshooting guide

##### You switched from unicorn to puma or puma to unicorn and the site is
dead

Chances are you're deploying with tags so the entire role did not run. When
you switch servers nginx needs to be restarted. Make sure you `-t nginx` or
just run the whole role when you change servers.

##### You can't clone your repo

Since the role needs to pull in from your git repo then it needs permission
to your repo. The most common way to do that is to setup an API access
token for GitHub.

GitLab is also supported, all of this is documented in the
[defaults/main.yml](https://github.com/ginas/ginas/blob/master/playbooks/roles/ginas.rails_deploy/defaults/main.yml)
file.

##### How would you go about setting up a CI platform with this role?

Rather than impose a CI solution on you, you're free to do whatever you want.

A possible situation might be to use this role to deploy to
a staging/CI/build server instead of directly to production. Now your build
server can run tests and push to production using this role on different
hosts if everything goes well.

That would allow you to have a sweet CI setup where your developers only
have to git push somewhere and minutes later you have tested code in
production if you don't have to worry about a ton of red tape.

### Authors and license

`rails_deploy` role was written by:

- Nick Janetakis | [e-mail](mailto:nick.janetakis@gmail.com) | [Twitter](https://twitter.com/nickjanetakis) | [GitHub](https://github.com/nickjj)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))

***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).
