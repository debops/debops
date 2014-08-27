### What does this role do?

It allows you to monitor services and receive e-mail/sms notifications when
an event happens.

### Getting started

You can use this role in 1 of 2 ways. As a dependency of another role or just by
configuring it in your inventory for a certain host/group/etc..

#### Using it as a dependency

```
# your_role/meta.main.yml

---

dependencies:

  - role: debops.monit
    monit_process_host_list:
      - pid: '/some/pid/path/foo.pid'
        script: '{{ your_role_monit_script }}'
    tags: monit
```

#### inventory/hosts

```
[debops_monit]
somehost
```

#### inventory/host_vars/somehost.yml

```
monit_process_host_list:
  - pid: '/some/pid/path/foo.pid'
```

### What are a few features available in this role?

- Receive e-mails or SMS notifications of events.
- Scope your process list by all servers, groups or single hosts.
- Optionally disable monit.
- Configure all of the mail details as you would expect.
  - Check the `defaults/main.yml` file for the details.

### License

[GPLv3](https://www.gnu.org/licenses/quick-guide-gplv3.html)

### Authors

`debops.monit` was created by:
- Nick Janetakis nick.janetakis@gmail.com
