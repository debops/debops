Custom versions
===============

Discourse
---------

FIXME: We `stable` is a branch, not the latest release on this branch!

The official Discourse Docker image defaults to the `tests-passed`_ branch.
``debops.discourse`` takes a more conservative default and installs the `latest
stable Discourse release`_. To override the default, add the something like
this to ``group_vars/debops_service_discourse.yml``:

.. code-block:: yaml

    # This can be any git commit hash, branch or tag.
    discourse_version: "stable"

    # Examples:
    #discourse_version: "tests-passed"
    #discourse_version: "latest-release"
    #discourse_version: "v1.4.0.beta6"
    #discourse_version: "5e38512b1b28382746d0826dbee9ffc7d6bd4ef5"

.. _tests-passed: https://github.com/discourse/discourse/tree/tests-passed
.. _latest stable Discourse release: https://github.com/discourse/discourse/tree/stable


Todo
--------------

* Implement installation of plugins

* Implement setting up a admin user with password.

* Implement updating based on discourse_release.

* Implement backup before updating.

* Verify discourse to ot provide any database migration step.

* Improve check for "is updated", based on ``git rev-parse`` - liek
  dicsourse_docker/launcher does when rebuilding.

* Scale db_shared_buffers and unicorn_workers based on physical CPU
  cores and memory like discourse_docker/discourse-setup does. Or
  provides some recommendations about values.

* Make unicorn listen on a Unix socket instead of a network port. See
  :file:`discourse/config/unicorn.conf.rb`.

* Implement these config vars:

  * rtl_css = true -> add "rtlit" gem
  * relative_url_root

* Enable proxy_cache for nginx. This requies some means of adding a
  line line this to the http-level of ngin (from the debobs.discourse
  role):

    proxy_cache_path /var/nginx/cache \
        keys_zone={{ discourse__nginx_upstream }}:10m max_size=200m;

* Ass nginx support for brotli comression. This requires building a
  custom version of nginx as Debian buster does not provide brotli.


Unicorn
-------------

RAILS_ENV *muss* gesettz sein für unicorn

unicorn.conf.rb:

worker_processes (ENV["UNICORN_WORKERS"] || 3).to_i
# listen "#{discourse_path}/tmp/sockets/unicorn.sock"
listen (ENV["UNICORN_PORT"] || 3000).to_i

pid UNICORN_PID_PATH
UNICORN_SIDEKIQS
UNICORN_SIDEKIQ_MAX_RSS


Redis
______________

passende variablen patchen (line_in_file)

   -daemonize no
   -appendonly no
   -databases 16
   +pidfile /home/pacs/xyz00/users/discourse/redis/run/redis-server.pid
   +port 32002
   +tcp-backlog 128
   +bind 127.0.0.1
   dbfilename dump.rdb
   dir /home/pacs/xyz00/users/discourse/redis/lib
   logfile /home/pacs/xyz00/users/discourse/redis/log/redis.log
   +loglevel notice
   +save 300 10
   +save 60 10000
   +save 900 1
   +slave-serve-stale-data yes
   -timeout 300



Postgresql
--------------
datestyle = 'iso, mdy'
default_text_search_config = 'pg_catalog.english'
lc_* = 'C.UTF-8'   locale settings
listen_addresses
ssl_cert_file
timezone


discourse install
------------------------

hostsharing:
   gem install bundler
   bundle install -j$(getconf _NPROCESSORS_ONLN) --deployment
   --without development test

   RAILS_ENV=production bundle exec rake secret

Relevant cronjobs
---------------------

- logrotate, sysstat, fstrim
- /var/lib/postgresql/take-database-backup (inactive)


Results of the Bootstrap Process Analysis
==========================================

* :file:`/var/www/discourse/config/discourse.conf` can be used for
  configuring discourse. But some tools (e.g. `cache_critical_dns`,
  which is not required) still require configuration variables.

* Unicorn and ruby need to be configured using some environment
  variables.

* Postgres is started using::

    HOME=/var/lib/postgresql USER=postgres \
    thpoff chpst -u postgres:postgres:ssl-cert -U postgres:postgres:ssl-cert \
           /usr/lib/postgresql/10/bin/postmaster -D /etc/postgresql/10/main

* Redis is started using::

    thpoff chpst -u redis -U redis /usr/bin/redis-server /etc/redis/redis.conf

* Unicorn is started (after starting redis and postgres) using::

    cd /var/www/discourse
    chown -R discourse:www-data /shared/log/rails
    LD_PRELOAD=$RUBY_ALLOCATOR HOME=/home/discourse USER=discourse \
    thpoff chpst -u discourse:www-data -U discourse:www-data \
    bundle exec config/unicorn_launcher -E production -c config/unicorn.conf.rb


Analysis of the Bootstrap Process
==========================================

Main insights:

* Environment variables and parameters can be found in the `pups` and
  container templates.

* Relevant parameters can be found in the `pups` and container
  templates.

* Relevant files for starting the services can be found in /etc/service
  in the docker container. These are either from :file:`image/base/`
  or are generated be some `pups` templates.

* Installation steps can be found in :file:`image/base/Dockerfile` and
  the `pups` templates.

* :file:`/var/www/discourse/config/discourse.conf` is generated from
  the enironment variables starting with ``DISCOURSE_``, overwriting
  the file if it already exists.


Summary:

* samples/standalone.yml is the main template for the all-in-one,
  standalone Discourse Docker container.

  For creating the debops role, samples/web_only.yml could be used,
  since the role will reuse existing debops roles for redis and
  postgres.

* The container template lists `pups` templates in the ``templates:``
  section. These `pups` templates are the actual installation
  instructions.

* Environment variables are merged from the `pups` templates and the
  container template (highest priority).

* Most configuration parameters for the container are passed via
  environment variables on the commend line when starting the
  container (via `launcher`). Only very few parameters are defined in
  the base image (see :file:`image/base/Dockerfile`).

  The environment can be queries from the build container using::

    docker inspect local_discourse/app | less -S

* `discourse_docker/launcher` queries the `pups` and container
  templates to construct the command line arguments for docker.



discourse_docker/discourse-setup (without any parameters)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-> no parameters -> one container setup
-> "two container setup is currently unsupported"
- checks resources and requirements
- if containers/apps.yml does not exist:
  - copies from samples/standalone.yml
  - scales db_shared_buffers and unicorn_workers based on physical CPU
    cores and memory
- asks user for config
- writes config file containers/apps.yml
- verifies relevant parameters have been changed (as compared to
  samples/standalone.yml)
- rebuilds container (via "./launcher rebuild app")


discourse_docker/launcher
~~~~~~~~~~~~~~~~~~~~~~~~~~

-> tool for building, running and accessing the docker images
-> reads config from containers/apps.yml ("app" is 2nd parameter
   passed to launcher)
-> Most config parameters for discourse are passed to the container
   via enironment variables. Most of these are not part of the
   image, but passed via launcher.

   User ``docker inspect local_discourse/app | less -S`` to learn
   which environment variables are set.


``launcher rebuild app`` (as called from discourse-setup)
-------------------------------------------------------------

- checks prerequisites

- updates itself if required (git pull)

- installs docker if none or a too old version is installed

- optionally runs additionnal commands in the container ("host_run") -
  currently not used be any provided config. Not sure what this is
  used for. Curiously this is done within the container while the
  image is not yet downloaded

- downloads discourse docker image (discourse/base)

- fetches from containers/apps.yml:

  - recursivly collects used `pups` templates. Per default these are

     - "templates/postgres.template.yml"
     - "templates/redis.template.yml"
     - "templates/web.template.yml"
     - "templates/web.ratelimited.template.yml"

  - from these templates plus :file:`containers/apps.yml`, collect:
    environment variables, labels for docker, expose-ports for docker
  - name of base_image, update_pups (default: yes)
  - volumes, links, run_image, boot_command, custom docker_args, hostname

- runs `pups` in the container - this will actually install discourse
  in the container

- save the state of the bootstrap container as "local_discourse/app"
   ("app" is 2nd parameter passed to launcher)

- start the container


Analysis of the Dockerfile for discourse/base
================================================

  - haproxy
  - advancecomp jhead jpegoptim libjpeg-turbo-progs optipng
  - ruby-build
  - gem update; gem install bundler
  - tphoff
  - ngx_brotli - brotli comression for nxinx
  - ENV RAILS_ENV production


- Installs postgresql 10 from apt.postgresql.org
- Installs node.js 10.x from deb.nodesource.com
  [buster: 10.15.2]

    nodejs
    node-uglify-js@<3 [busgter: 3.4]"
    svgo [missing in buster]

* Installs jhead, jpegoptim, libjpeg-turbo-progs, optipng,
  pngcrush 1.8.13 [buster: 1.8.13], gifsicle 1.92 [buster: 1.91],
  pngquant 2.12.3 [buster: 2.12.2] libpng 1.6.37 [buster: 1.6.36],
  imagemagick 7.0.8-50 [buster: imagemagick-6.q16 6.9.10]

libmagickcore-6.q16-6-extra

  - redis 5.0.5:
      - user: redis:redis /var/lib/redis
      - benutzt standard config von redis source
    - daemoinze no !
    - logfile "" !
    - protected-mode no ! was ist das?
    - #bind

  - ENV RUBY_ALLOCATOR /usr/lib/libjemalloc.so.1:
      - stable: https://github.com/jemalloc/jemalloc/releases/download/3.6.0/
      - new: https://github.com/jemalloc/jemalloc/releases/download/5.2.0/

haproxy monit socat -- what is this used for?

jemalloc-3.6.0.tar.bz2 # "stabile" <-- discourse uses this one
jemalloc-5.2.0.tar.bz2 # new [buster: 5.1.0]
ENV RUBY_ALLOCATOR /usr/lib/x86_64-linux-gnu/libjemalloc.so.2  # FIXME: platform!

  - ngx_brotli - brotli comression for nxinx

- ruby 2.6.3 (via ruby-build) [buster: 2.5.1]

gem, bundler, pups

- Builds nginx 1.16.0 with brotil-support
  If we would woant to install this, too, here are isntruction for how
  to do in stretch (using Debian methids):
  https://medium.com/@wintermeyer/nginx-with-brotli-on-debian-stretch-2917b1147aec


- Installs redis 5.0.5
- Add `redis` user and group with home=/var/lib/redis
cp /tmp/redis-$REDIS_VERSION/redis.conf /etc/redis



* Build-Flags for imagemagick are in install-imagemagick:
  Imagemagick is build with

   --enable-static #
   --enable-bounds-checking ---
   --enable-hdri ----
   --enable-hugepages ---
   --with-threads ?
   --with-modules #
   --with-quantum-depth=16 #
   --without-magick-plus-plus -
   --with-bzlib #
   --with-zlib #
   --without-autotrace #
   --with-freetype #
   --with-jpeg #
   --with-lzma #
   --with-png #
   --with-tiff #
   --without-lcms #

  Flags used to build can be found in the build-logs:
  https://buildd.debian.org/status/logs.php?pkg=imagemagick&arch=amd64

ruby requires modules png tiff jpeg freetype modules

# This tool allows us to disable huge page support for our current process
# since the flag is preserved through forks and execs it can be used on any
# process
ADD thpoff.c /src/thpoff.c
RUN gcc -o /usr/local/sbin/thpoff /src/thpoff.c && rm /src/thpoff.c

useradd discourse -s /bin/bash -m -U  # no home, with user-group

- /checks out discours from git into /var/www/discourse/
  (owned by discourse:discourse

- Aus user discourse:
    bundle install --deployment --jobs 4 --without test development
    bundle exec rake maxminddb:get
    find /var/www/discourse/vendor/bundle -name tmp -type d -exec rm -rf {}


Hostsharing (discourse ):
  - install redis:
    - daemoinze no
    - nur localhost
    - tcp-backlog 128
    - databases 16
    - irgendwelche "save" parameter
  - install discourse:
      - Konfig:
          - db_host, db_port von postgresql  - besser: über socket
          - redis_host von redis  - besser: über socket
          - kein db_backup_port
          - hostname !
          - smtp_*
  - Sidekiq für Hintergrund-Aufgaben konfigurieren:
      - nicht näher beschrieben
  - DB initialisieren
  - Assets kompilieren
  - Webserver konfig
  - system start (nehmen supervisor)



Installing the docker images inside a VM
==============================================

`discourse_docker` provides a `Vagrantfile` which can be use to test
the container setup. Here is how to use it.::

  vagrant up --no-provision
  vagrant ssh

In the VM::

  sudo bash
  apt-get update
  apt-get install --yes docker.io

  # Not tested whether building the image ourself avoids pulling it
  # from docker-hub.
  apt install --yes ruby
  cd /vagrant/image
  ruby auto_build.rb base

  cd /vagrant
  ./discourse-setup  # fill in some reasonable values!

To get a shell within the container, run::

  sudo /vagrant/launcher run app bash --docker-args -it
