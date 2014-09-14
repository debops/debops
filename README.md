## elasticsearch

[![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg?style=flat)](#)


`debops.elasticsearch` role allows you to easily setup infrastructure
capable of running Elasticsearch.

#### What are a few features available in this role?

- Seamless clustering
- Easily pick node types through groups and also allow you to do it manually
- Add/Remove plugins and libs on demand
  - You can even set custom configuration to each plugin, check the defaults
- Tweak pretty much everything that ES allows you to



### Role dependencies

- `debops.etc_services`
- `debops.ferm`
- `debops.java`



### Role variables

List of default variables available in the inventory:

    ---
    # role: elasticsearch
    
    
    # NOTE: For the details on what each variable does, please see comments in the
    # default Elasticsearch configuration file:
    # https://github.com/elasticsearch/elasticsearch/blob/master/config/elasticsearch.yml
    
    
    # ---- Inventory group names ----
    
    elasticsearch_group_master: 'debops_elasticsearch_master'
    elasticsearch_group_workhorse: 'debops_elasticsearch_workhorse'
    elasticsearch_group_coordinator: 'debops_elasticsearch_coordinator'
    elasticsearch_group_loadbalancer: 'debops_elasticsearch_loadbalancer'
    
    
    # ---- DebOps role dependencies ----
    
    # Automatically install Java 7 Open JDK JRE.
    elasticsearch_role_dependencies: ['java']
    
    
    # ---- Version ----
    
    # It will automatically install the latest minor release, only supply 1.x.
    elasticsearch_version: '1.3'
    
    
    # ---- Cluster ----
    
    elasticsearch_cluster_name: 'elasticsearch'
    
    
    # ---- Node ----
    
    # An empty name will let elasticsearch randomly generate one for you.
    elasticsearch_node_name: ''
    
    elasticsearch_node_master: true
    elasticsearch_node_data: true
    elasticsearch_node_rack: 'nicerack'
    elasticsearch_node_max_local_storage_nodes: 50
    
    
    # ---- Index ----
    
    elasticsearch_index_shards: 5
    elasticsearch_index_replicas: 1
    
    
    # ---- Plugins ----
    
    # Examples:
    #
    # It follows the same syntax as using the ES plugin manager:
    # bin/plugin -i <name> -u <url>
    #
    # The url and config is optional.
    #
    #
    # Using only a name...
    #
    #elasticsearch_plugins:
    #  - name: 'com.sksamuel.elasticsearch/elasticsearch-river-redis/1.1.0'
    #
    #elasticsearch_plugins:
    #  - name: 'com.sksamuel.elasticsearch/elasticsearch-river-redis/1.1.0'
    #    delete: True
    #
    #
    # Using a name with url...
    #
    #elasticsearch_plugins:
    #  - name: 'facet-script'
    #    url: 'http://dl.bintray.com/content/imotov/elasticsearch-plugins/elasticsearch-facet-script-1.1.2.zip'
    #
    #
    # Using a name and custom configuration (in this case, cloud-aws)...
    # Just pass a string block to the config key, it works for any plugin.
    #
    #elasticsearch_plugins:
    #  - name: elasticsearch/elasticsearch-cloud-aws/2.3.0
    #    config: |
    #    # cloud-aws configuration
    #      cloud:
    #        aws:
    #          access_key: <your access key>
    #          secret_key: <your secret key>
    #      discovery:
    #        type: ec2
    #      repositories:
    #        bucket: <the bucket created in s3>
    
    # A list of plugins to install or delete.
    elasticsearch_plugins: []
    
    
    # ---- Libraries ----
    
    # Examples:
    #
    # The url is required, everything else is optional.
    #
    #
    #elasticsearch_libs:
    #  url: 'http://somewebsite.com/foo.jar'
    #
    #
    #elasticsearch_libs:
    #  url: 'http://somewebsite.com/foo.jar'
    #  file: 'differentfilename.jar'
    #  delete: True
    #
    #
    #elasticsearch_libs:
    #  url: 'http://somewebsite.com/foo.jar'
    #  user: 'basicauthuser'
    #  pass: 'basicauthpass'
    
    # A list of libraries to install or delete.
    elasticsearch_libs: []
    
    
    # ---- Memory and filesystem ----
    
    elasticsearch_memory_mlockall: false
    
    # The heap size should be about 50% of your total RAM on a dedicated instance.
    # If you are running ES with a bunch of other services don't be afraid to
    # drastically lower this but be aware of performance issues if it's too low.
    elasticsearch_memory_heap_size_multiplier: 0.5
    
    elasticsearch_memory_heap_newsize: ''
    elasticsearch_memory_direct_size: ''
    elasticsearch_memory_locked_size: 'unlimited'
    elasticsearch_memory_vma_max_map_count: 262144
    elasticsearch_fs_max_open_files: 65535
    
    # Force ES to use ipv4, set this to an empty string if you want to use ipv6.
    elasticsearch_fs_java_opts: '-Djava.net.preferIPv4Stack=true'
    
    
    # ---- Network and HTTP ----
    
    elasticsearch_bind_host: 'localhost'
    elasticsearch_publish_host: '{{ ansible_default_ipv4.address }}'
    elasticsearch_node_port: '9300-9400'
    elasticsearch_http_port: '9200-9300'
    
    elasticsearch_compress: false
    elasticsearch_http_max_content_length: '100mb'
    elasticsearch_http_enabled: true
    
    # Which hosts are allowed to connect through the firewall?
    
    # This is used for inter-node communication and in multicast's case, discovery.
    elasticsearch_node_allow: []
    elasticsearch_multicast_allow: '{{ elasticsearch_node_allow }}'
    
    # This is used for accessing the http API, you may consider having your app
    # servers be able to access it, etc..
    elasticsearch_http_allow: []
    
    
    # ---- Security ----
    
    # Do not enable this unless you have a very good reason to do so.
    elasticsearch_jsonp_enabled: false
    
    
    # ---- Gateway ----
    
    elasticsearch_gateway_type: 'local'
    
    # These get dynamically set by ES, make sure you know what you're doing.
    #elasticsearch_gateway_recover_after_time: ?
    #elasticsearch_gateway_recover_after_nodes: ?
    #elasticsearch_gateway_expected_nodes: ?
    
    
    # ---- Recovery throttling ----
    
    elasticsearch_recovery_max_bytes_per_sec: '20mb'
    
    # These get dynamically set by ES, make sure you know what you're doing.
    #elasticsearch_recovery_node_initial_primaries_recoveries: ?
    #elasticsearch_recovery_node_concurrent_recoveries: ?
    #elasticsearch_recovery_concurrent_streams: ?
    
    
    # ---- Discovery ----
    
    # Consider raising this once you have > 2 nodes.
    elasticsearch_discovery_minimum_master_nodes: 1
    
    elasticsearch_discovery_ping_timeout: '3s'
    elasticsearch_discovery_multicast_enabled: true
    elasticsearch_discovery_ping_unicast_hosts: []
    
    
    # ---- Slow log ----
    
    elasticsearch_slowlog_query_warn: '10s'
    elasticsearch_slowlog_query_info: '5s'
    elasticsearch_slowlog_query_debug: '2s'
    elasticsearch_slowlog_query_trace: '500ms'
    
    elasticsearch_slowlog_fetch_warn: '1s'
    elasticsearch_slowlog_fetch_info: '800ms'
    elasticsearch_slowlog_fetch_debug: '500ms'
    elasticsearch_slowlog_fetch_trace: '200ms'
    
    elasticsearch_slowlog_index_warn: '10s'
    elasticsearch_slowlog_index_info: '5s'
    elasticsearch_slowlog_index_debug: '2s'
    elasticsearch_slowlog_index_trace: '500ms'
    
    
    # ---- GC Logging ----
    
    elasticsearch_monitor_gc_young_warn: '1000ms'
    elasticsearch_monitor_gc_young_info: '700ms'
    elasticsearch_monitor_gc_young_debug: '400ms'
    
    elasticsearch_monitor_gc_old_warn: '10s'
    elasticsearch_monitor_gc_old_info: '5s'
    elasticsearch_monitor_gc_old_debug: '2s'
    
    
    # ---- Logging ----
    
    elasticsearch_logger_level: 'INFO'
    elasticsearch_logger_output: '{{ elasticsearch_logger_level }}, console, file'
    
    elasticsearch_logger:
      action: 'DEBUG'
      amazon_aws: 'WARN'
      gateway: 'DEBUG'
      index_gateway: 'DEBUG'
      indices_recovery: 'DEBUG'
      discovery: 'TRACE'
      index_search_slowlog: 'TRACE, index_search_slow_log_file'
      index_indexing_slowlog: 'TRACE, index_indexing_slow_log_file'
    
    elasticsearch_logger_additivity:
      index_search_slowlog: false
      index_indexing_slowlog: false
    
    elasticsearch_logger_appender:
      console:
        type: console
        layout:
          type: consolePattern
          conversionPattern: '[%d{ISO8601}][%-5p][%-25c] %m%n'
      file:
        type: dailyRollingFile
        file: ${path.logs}/${cluster.name}.log
        datePattern: "'.'yyyy-MM-dd"
        layout:
          type: pattern
          conversionPattern: '[%d{ISO8601}][%-5p][%-25c] %m%n'
      index_search_slow_log_file:
        type: dailyRollingFile
        file: ${path.logs}/${cluster.name}_index_search_slowlog.log
        datePattern: "'.'yyyy-MM-dd"
        layout:
          type: pattern
          conversionPattern: '[%d{ISO8601}][%-5p][%-25c] %m%n'
      index_indexing_slow_log_file:
        type: dailyRollingFile
        file: ${path.logs}/${cluster.name}_index_indexing_slowlog.log
        datePattern: "'.'yyyy-MM-dd"
        layout:
          type: pattern
          conversionPattern: '[%d{ISO8601}][%-5p][%-25c] %m%n'




### Detailed usage guide

Below is a breakdown of how you can use groups to allocate different node
types to a number of servers. If all you want to do is use ES as a single
server dependency in another role then include the role in your role's
meta main file. You don't have to add the groups in your inventory in that case.

#### hosts

Elasticsearch has 2 settings, `node.master` and `node.data`. A combination
of those settings being true or false  determines what type of node your
server will be.

##### Master servers (`node.master: true` and `node.data: true`)

This is the default setting for all nodes in elasticsearch.

```
[debops_elasticsearch_master]
apple
orange
banana
```

##### Workhorse servers (`node.master: false` and `node.data: true`)

The server will never become a master but it will hold data.

```
[debops_elasticsearch_workhorse]
red
blue
```

##### Coordinator servers (`node.master: true` and `node.data: false`)

A coordinator can become master but it doesn't store data. Its goal is to always
have a lot of free resources.

```
[debops_elasticsearch_coordinator]
nyancat
```

##### Search load balancer servers (`node.master: false` and `node.data: false`)

A server of this type would be used to fetch data from other servers,
aggregate results, etc..

```
[debops_elasticsearch_loadbalancer]
judge
jury
```

##### Grouping them all up

It's always useful to have a common group that composes everything.
Elasticsearch will be installed on any server that belongs to any of the above groups.

This group would mainly be used for firewall settings which would apply to
all of your ES nodes. It does not control whether or not ES gets installed.

```
[debops_elasticsearch:children]
debops_elasticsearch_master
debops_elasticsearch_workhorse
debops_elasticsearch_coordinator
debops_elasticsearch_loadbalancer
```

#### What's with all of the groups?

They are just shortcuts to setting the 2 node settings for you. You don't
have to use the extra groups. By all means create custom groups and set the
variables yourself if you want.

You can also edit the defaults to use your own custom group names and still
get the benefits of group based node type separation.

#### inventory/group_vars/debops_elasticsearch.yml

```
elasticsearch_bind_host: ['0.0.0.0']
elasticsearch_node_allow: '{{ groups["debops_elasticsearch"] }}'
elasticsearch_http_allow: '{{ groups["your_web_apps"] }}'

# The above example tells ES to accept connections from anywhere and then
# white lists your ES group so they can all talk to each other

# In addition to that is white lists your app servers so they can access the
# ES HTTP API to actually query ES
```

### Authors and license

`elasticsearch` role was written by:

- Nick Janetakis | [e-mail](mailto:nick.janetakis@gmail.com) | [Twitter](https://twitter.com/nickjanetakis) | [GitHub](https://github.com/nickjj)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)

***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).
