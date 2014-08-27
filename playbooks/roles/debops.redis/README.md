### What does this role do?

It allows you to easily setup infrastructure capable of running and managing 1 or more redis servers. It is completely self healing with redis sentinel and supports replication seamlessly.

### Getting started

Below is the bare minimum to get started to setup a few redis servers acting together. If all you want to do is use redis as a single server dependency in another role then include the role in your role's meta main file. You don't have to add the groups in your inventory in that case.

#### hosts

```
[debops_redis]
foo
bar
baz

# In the above example the 'foo' host would be the redis master and everything
# else would be a slave of that master.

[debops_redis_sentinel]
qux

# You can have 1 or more sentinels. The sentinel(s) will control your master
# and slave relationships.
```

#### inventory/group_vars/debops_redis_sentinel.yml

```
redis_sentinel_bind: ['0.0.0.0']
redis_sentinel_allow: ['192.168.0.0/16']

# In the above example it is expected you have ferm running to block all ports.
# The above example tells redis to accept connections from anywhere and then
# white lists your local network to allow connections to it.
```

#### inventory/group_vars/debops_redis.yml

```
redis_bind: ['0.0.0.0']
redis_server_allow: '{{ groups["your_web_apps"] + redis_sentinel_hosts_group }}'

# The setup above allows you to grant access to your redis servers from your
# application group and the sentinel group. You can add as many hosts as you need.
```

If you want a sentinel server to also act as a redis server you can combine the 2 iservices on 1 host. You will need to set `redis_sentinel_standalone: False` in that host's inventory. This is covered in the `defaults/main.yml` file.

#### playbook

```
# You don't need to define a playbook unless you want to use group names other
# than the default. If you use non-default group names then make sure you
# change the defaults in your inventory.
```

#### Running the playbook

`./site.sh -t redis`

### What are a few features available in this role?

- Seamless master/slave replication
- Throw together a master + n slaves + n sentinel setup in about 10 lines of yaml
   - Most of those lines would be adding your hosts to the inventory!
- Your configs are idempotent, even when redis rewrites them
- Pretty much every redis config value is tweakable
- You can easily use this role as a dependency in your other roles

### License

[GPLv3](https://www.gnu.org/licenses/quick-guide-gplv3.html)

### Authors

`debops.redis` was created by:
- Nick Janetakis nick.janetakis@gmail.com
- Maciej Delmanowski drybjed@gmail.com
