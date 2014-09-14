
## [![DebOps project](http://debops.org/images/debops-small.png)](http://debops.org) nginx



[![Travis CI](http://img.shields.io/travis/debops/ansible-nginx.svg?style=flat)](http://travis-ci.org/debops/ansible-nginx) [![test-suite](http://img.shields.io/badge/test--suite-ansible--nginx-blue.svg?style=flat)](https://github.com/debops/test-suite/tree/master/ansible-nginx/)  [![Ansible Galaxy](http://img.shields.io/badge/galaxy-debops.nginx-660198.svg?style=flat)](https://galaxy.ansible.com/list#/roles/1580) [![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg?style=flat)](#)






[nginx](http://nginx.org/) is a fast and light webserver with extensible
configuration.

`debops.nginx` role can be used to install and manage `nginx` configuration
for multiple websites at the same time. Server is configured using
inventory variables, role can also be used as a dependency of another role
to configure a webserver for that role using dependency variables.





### Installation

This role requires at least Ansible `v1.7.0`. To install it, run:

    ansible-galaxy install debops.nginx

#### Are you using this as a standalone role without DebOps?

You may need to include missing roles from the [DebOps common
playbook](https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml)
into your playbook.

[Try DebOps now](https://github.com/debops/debops) for a complete solution to run your Debian-based infrastructure.





### Role dependencies

- `debops.apt_preferences`
- `debops.ferm`





### Role variables

List of default variables available in the inventory:

    ---
    
    # List of IP addresses or CIDR networks allowed to connect to HTTP or HTTPS
    # service. It will be configured in iptables firewall via 'ferm' role. If there
    # are no entries, nginx will accept connections from any IP address or network.
    # If you have multiple web services on a host, you might want to control access
    # using 'item.location_allow' option instead.
    nginx_allow: []
    nginx_group_allow: []
    nginx_host_allow: []
    
    nginx_base_packages: [ 'nginx-full' ]
    nginx_user: 'www-data'
    
    # Nicenness, from 20 (nice) to -20 (not nice)
    nginx_worker_priority: '0'
    
    nginx_worker_processes: '{{ ansible_processor_cores }}'
    nginx_worker_connections: 1024
    
    # Maximum number of opened files per process, must be higher than worker_connections
    nginx_worker_rlimit_nofile: 4096
    
    nginx_server_tokens: 'off'
    
    nginx_server_names_hash_bucket_size: 64
    nginx_server_names_hash_max_size: 512
    
    nginx_default_keepalive_timeout: 60
    
    # Path to PKI infrastructure, set to False to disable nginx SSL support
    nginx_pki: '/srv/pki'
    
    # SSL key hostname to look for to check if SSL should be enabled
    nginx_pki_check_key: '{{ ansible_fqdn }}'
    
    # Where to look for certificate by default, choices: 'selfsigned', 'signed', 'wildcard'
    # Server-wide.
    nginx_default_ssl_type: 'selfsigned'
    
    # Default hostname used to select SSL certificate if none is defined
    nginx_default_ssl_cert: '{{ ansible_fqdn }}'
    
    # Default SSL cipher list. More information in vars/main.yml
    nginx_default_ssl_ciphers: 'pfs'
    
    # Default SSL ECDH curve used on servers, to see a list of supported curves, run:
    #     openssl ecparam -list_curves
    # See also: https://security.stackexchange.com/questions/31772/
    nginx_default_ssl_curve: 'secp384r1'
    
    # If wildcard SSL certificate is used, which one should be used by default?
    nginx_default_ssl_wildcard: '{{ ansible_domain }}'
    
    # List od DNS servers used to resolve OCSP stapling. If it's empty, nginx role
    # will try to use nameservers from /etc/resolv.conf
    # Currently only the first nameserver is used
    nginx_ocsp_resolvers: []
    
    # At what hour run DH params regeneration script?
    nginx_cron_dhparams_hour: '1'
    
    # HTTP Strict-Transport-Security
    # https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security
    nginx_hsts_age: '15768000'
    nginx_hsts_subdomains: True
    
    # server_name which will be marked as default
    nginx_default_name: '{{ ansible_fqdn }}'
    
    # Default server template used if no type is selected
    nginx_default_type: 'default'
    
    # Default server root
    nginx_default_root: '/srv/www/sites/default/public'
    
    # Create global webroot directories?
    # Path: /srv/www/sites/*/public
    nginx_webroot_create: True
    nginx_webroot_owner: 'root'
    nginx_webroot_group: 'root'
    nginx_webroot_mode: '0755'
    
    # Should nginx servers have status pages enabled by default
    # If yes, provide a list of allowed networks/hosts
    #nginx_default_status:
    #  - '127.0.0.0/8'
    
    # Hash of symlinks to local server definitions stored in /etc/nginx/sites-local/
    # Entries with empty values or False will be removed
    # Symlinks will be created in /etc/nginx/sites-enabled/
    nginx_local_servers: {}
      #'symlink': 'file'
      #'other-symlink.conf': 'sub/directory/file.conf'
      #'removed-file': False
      #'also-removed':
      #'symlink\ with\ spaces.conf': 'other-file.conf'
    
    # Should nginx role generate upstream definitions?
    nginx_manage_upstreams: True
    
    # List of nginx upstream definitions
    nginx_upstreams: [ '{{ nginx_upstream_php5 }}' ]
    
    # Upstream for default php5-fpm configuration
    nginx_upstream_php5:
      enabled: True
      name: 'php5_www-data'
      type: 'php5'
      php5: 'www-data'
    
    # Should nginx role generate server definitions?
    nginx_manage_servers: True
    
    # List of nginx server definitions
    nginx_servers: [ '{{ nginx_server_default }}' ]
    
    # Default nginx site - options commented out are optional
    nginx_server_default:
      enabled: True
      name: []
      default: True
      #by_role: ''
      #locked: False
      #userdir: False
      #type: 'default'
      #redirect: 'http://other.example.com/'
      #redirect_ssl: 'http://other.example.com/'
      #redirect_code: '307'
      #redirect_from: False/True or []
      #ssl: True
      #ssl_type: 'selfsigned'
      #ssl_ciphers: 'pfs'
      #ssl_curve: 'secp384r1'
      #ssl_name: '{{ ansible_fqdn }}'
      #ssl_cert: '/path/to/server/certificate.crt'
      #ssl_key: '/path/to/server/keyfile.key'
      #owner: 'root'
      #group: 'root'
      #keepalive: 60
      #favicon: True
      #listen:
      #  - '80'
      #listen_ssl:
      #  - '443'
      #root: '{{ nginx_default_root }}'
      #status:
      #  - '127.0.0.0/8'
      #options: |
      #  # Literal text block;
      #  # With options;
      #error_pages:
      #  '404': '/404.html'
      #location: |
      #  '/':
      #    try_files $uri $uri/ $uri.html $uri.htm /index.html /index.htm =404;
      #  '/doc/': |
      #    alias /usr/share/doc/;
      #    autoindex on;
      #location_allow:
      #  '/doc/':
      #    - '127.0.0.1'
      #    - '::1'
      # location_allow without corresponding location_deny implies deny all
      #location_deny:
      #  '/doc/':
      #    - 'all'
      #location_referers:
      #  '/': [ '{{ ansible_fqdn }}', 'www.{{ ansible_fqdn }}', '*.{{ ansible_domain }}' ]
      #location_list:
      #  - pattern: '/'
      #    pattern_prefix: ''  # for example, '@' to have 'location "@pattern"'
      #    referers: [ '{{ ansible_fqdn }}', 'www.{{ ansible_fqdn }}', '*.{{ ansible_domain }}' ]
      #    allow: [ '127.0.0.1', '::1' ]
      #    deny: []
      #    options: |
      #      try_files $uri $uri/ $uri.html $uri.htm /index.html /index.htm =404;
      #    locations:
      #      - pattern: '/subdir'
      #
      # Additional parameters can be found in nginx server templates:
      #    templates/etc/nginx/sites-available/*.conf.j2



List of internal variables used by the role:

    nginx_ssl
    nginx_ocsp_resolvers






### Authors and license

`nginx` role was written by:

- Maciej Delmanowski | [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)



***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).
