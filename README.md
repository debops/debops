## redis

[![Travis CI](https://secure.travis-ci.org/debops/ansible-redis.png)](http://travis-ci.org/debops/ansible-redis) [![test-suite](http://img.shields.io/badge/test--suite-ansible--redis-blue.svg)](https://github.com/debops/test-suite/tree/master/ansible-redis/) [![Ansible Galaxy](http://img.shields.io/badge/galaxy-debops.redis-660198.svg)](https://galaxy.ansible.com/list#/roles/1592)[![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg)](#)

`debops.redis` role allows you to easily setup infrastructure capable of
running and managing 1 or more Redis servers. It is completely self healing
with Redis Sentinel and supports replication seamlessly.

Few features available in this role:

- seamless master/slave replication;
- throw together a master + n slaves + n sentinel setup in about 10 lines of YAML
  (most of those lines would be adding your hosts to the inventory);
- your configs are idempotent, even when redis rewrites them;
- pretty much every redis config value is tweakable;
- you can easily use this role as a dependency in your other roles;


### Installation

This role requires at least Ansible `v1.7.0`. To install it, run:

    ansible-galaxy install debops.redis



### Role dependencies

- `debops.secret`
- `debops.apt_preferences`
- `debops.etc_services`
- `debops.ferm`



### Role variables

List of default variables available in the inventory:

    ---
    
    # NOTE: Redis requires boolean variables to be exactly yes or no, do not confuse
    # them with yaml booleans. They should be quoted to be output as strings.
    
    # Check the URLs below for a detailed explanation of each command:
    # http://download.redis.io/redis-stable/redis.conf
    # http://download.redis.io/redis-stable/sentinel.conf
    
    
    # --- General ---
    
    # Which inventory group does redis-server belong to?
    redis_hosts_group: 'debops_redis'
    
    # What is the master redis server's host and port?
    # You can use a host name or IPv4 address.
    redis_hosts_master: '{{ groups[redis_hosts_group][0] }} {{ redis_port }}'
    
    # You might want to use 0.0.0.0 and then allow access from your app servers or
    # anything that needs to talk to redis by configuring redis_server_allow below.
    redis_bind: ['localhost']
    
    redis_port: 6379
    
    # Allow connections from a list of hosts, you may use masks such as:
    # 192.168.0.0/16 but it must be in a list, ex. ['192.168.0.0/16'].
    redis_server_allow: []
    
    redis_timeout: 0
    redis_tcp_keepalive: 0
    redis_tcp_backlog: 511
    redis_loglevel: 'notice'
    
    
    # ---- Sentinel ----
    
    # When set to False both redis-server and redis-sentinel will be on the same host.
    redis_sentinel_standalone: True
    
    # Which inventory group does redis-sentinel belong to?
    redis_sentinel_hosts_group: 'debops_redis_sentinel'
    
    # These values accept the same type of values as the general redis server.
    redis_sentinel_bind: ['localhost']
    redis_sentinel_port: 26379
    redis_sentinel_allow: []
    
    # A list of redis servers to monitor. Commented values are optional.
    redis_sentinel_group_list:
    # The name of the monitor group, you can use whatever you want.
      - name: 'main'
    # The master server's host address.
        #host: '{{ groups[redis_hosts_group][0] }}'
    # The master server's port.
        #port: '{{ redis_port }}'
    # How many sentinels need to agree that the master is down before failing over?
        #quorom: 2
    # Consult the redis documentation for the rest.
        #parallel_syncs: 1
        #down_after_milliseconds: 30000
        #failover_timeout: 180000
        #notification_script: ''
        #client_reconfig_script: ''
    
    
    # ---- Snapshotting ----
    
    # You can disable saving entirely by providing an empty list.
    redis_save:
      - '900 1'
      - '300 10'
      - '60 10000'
    
    redis_stop_writes_on_bgsave_error: 'yes'
    
    
    # ---- Replication ----
    
    redis_slave_read_only: 'yes'
    redis_repl_ping_slave_period: 10
    redis_repl_timeout: 60
    redis_repl_backlog_size: 1mb
    redis_repl_backlog_ttl: 3600
    redis_slave_priority: 100
    redis_min_slaves_to_write: 0
    redis_min_slaves_max_lag: 10
    
    
    # ---- Security ----
    
    redis_requirepass: False
    #
    # Example using the secret role to automatically set a password.
    # This password will be applied to the master, slaves and sentinels.
    #redis_requirepass: "{{ lookup('password', secret + '/credentials/' + groups[redis_hosts_group][0] + '/redis/redis/password length=20') }}"
    
    
    # ---- Limits ----
    
    redis_maxclients: 10000
    
    # Set a percent multiplier to cap the amount of RAM redis will use. For example
    # if you wanted to limit it to 80% of the total RAM you would input 0.8.
    redis_maxmemory_multiplier: 1.0
    
    redis_maxmemory_policy: 'volatile-lru'
    
    
    # ---- Append only mode ----
    
    redis_appendonly: 'no'
    
    
    # ---- Slow log ----
    
    redis_slowlog_log_slower_than: 10000
    redis_slowlog_max_len: 128
    
    
    # ---- Latency monitor ----
    
    redis_latency_monitor_threshold: 0
    
    
    # ---- Event notification ----
    
    redis_notify_keyspace_events: False




### Detailed usage guide

Below is the bare minimum to get started to setup a few Redis servers
acting together. If all you want to do is use Redis as a single server
dependency in another role then include the role in your role's meta main
file. You don't have to add the groups in your inventory in that case.

##### inventory/hosts

    # In this example the 'redis-server0' host would be the redis
    # master and everything else would be a slave of that master.
    [debops_redis]
    redis-server0
    redis-server1
    redis-server2
    
    # You can have 1 or more sentinels. The sentinel(s) will control your master
    # and slave relationships.
    [debops_redis_sentinel]
    redis-monitor

##### inventory/group_vars/debops_redis_sentinel.yml

    # It is expected that you have a firewall configured with 'debops.ferm'
    # role, set up to block all ports. Variables below tell Redis role to
    # accept connections from anywhere and then whitelist your local
    # network to allow connections to it.
    redis_sentinel_bind: ['0.0.0.0']
    redis_sentinel_allow: ['192.168.0.0/16']

##### inventory/group_vars/debops_redis.yml

    # This setup allows you to grant access to your redis servers from your
    # application group and the sentinel group. You can add as many hosts
    # as you need.
    redis_bind: ['0.0.0.0']
    redis_server_allow: '{{ groups["your_web_apps"] + redis_sentinel_hosts_group }}'

If you want a Sentinel server to also act as a Redis server you can combine
the 2 iservices on 1 host. You will need to set `redis_sentinel_standalone: False`
in that host's inventory. This is covered in the `defaults/main.yml` file.

You don't need to define a playbook unless you want to use group names other
than the default. If you use non-default group names then make sure you
change the defaults in your inventory.

##### Running the playbook

    ./site.sh -t redis

### Authors and license

`redis` role was written by:

- Nick Janetakis | [e-mail](mailto:nick.janetakis@gmail.com) | [Twitter](https://twitter.com/nickjanetakis) | [GitHub](https://github.com/nickjj)

- Maciej Delmanowski | [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))

***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).
