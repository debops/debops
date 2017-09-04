Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Use the correct subdomain variable in Postfix configuration. [drybjed]

- Expose the domain used by SMS gateway in role default variables. [drybjed]

- Restart ``smsd`` after configuration has changed, needed on ``systemd``-based
  systems. [drybjed]

- Move the hard role dependencies to an example Ansible playbook. [drybjed]

- Update the Postfix integration to support latest ``debops.postfix`` rewrite.
  [drybjed]
