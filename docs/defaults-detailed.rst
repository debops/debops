Default variable details
========================

Some of ``debops.unattended_upgrades`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _unattended_upgrades__ref_blacklist:

unattended_upgrades__blacklist
------------------------------

The :envvar:`unattended_upgrades__blacklist` and similar lists allow you to specify
packages which shouldn't be upgraded automatically. The lists can be nested. You
can specify them as simple package names or dictionaries with specific keys:

``name``
  Required, string or list specifying a package name to include in the
  blacklist.

``state``
  Required. Choices:

  ``present``
    The specified package(s) will be added in the blacklist.

  ``absent``
    The specified package(s) will be removed in the blacklist.

Examples
~~~~~~~~

Include specified packages in the upgrade blacklist on all hosts:

.. code-block:: yaml

   unattended_upgrades__blacklist:

     - 'zsh'

     - name: 'postgresql'
       state: '{{ "present" if (ansible_hostname in [ "database", "db" ]) else "absent" }}'

     - name: [ '^linux-.*', 'vim' ]
       state: '{{ "present"
                 if (ansible_local|d() and ansible_local.tags|d()
                     and "production" in ansible_local.tags)
                 else "absent" }}'


.. _unattended_upgrades__ref_origins:

unattended_upgrades__origins
----------------------------

The :envvar:`unattended_upgrades__origins` and
:envvar:`unattended_upgrades__dependent_origins` lists define origin patterns of
repositories that will be considered for unattended package upgrades.
The lists can be nested.
You can specify them as simple origin patterns or dictionaries with specific
keys:

``origin``
  Required, string or list of origin patterns.

  Alternatively, ``origins`` also works.

``state``
  Required. Choices:

  ``present``
    The specified origin patterns will be considered for unattended package upgrades.

  ``absent``
    The specified origin patterns will be not considered for unattended package upgrades.


Origins syntax
~~~~~~~~~~~~~~

.. Copied from the /etc/apt/apt.conf.d/50unattended-upgrades file.

Lines below have the format format is ``keyword=value,...``.  A
package will be upgraded only if the values in its metadata match
all the supplied keywords in a line.  (In other words, omitted
keywords are wild cards.) The keywords originate from the Release
file, but several aliases are accepted.  The accepted keywords are::

  a,archive,suite (eg, "stable")
  c,component     (eg, "main", "crontrib", "non-free")
  l,label         (eg, "Debian", "Debian-Security")
  o,origin        (eg, "Debian", "Unofficial Multimedia Packages")
  n,codename      (eg, "jessie", "jessie-updates")
    site          (eg, "http.debian.net")

The available values on the system are printed by the command
"apt-cache policy", and can be debugged by running
"unattended-upgrades -d" and looking at the log file.

Within lines unattended-upgrades allows 2 macros whose values are
derived from :file:`/etc/debian_version`::

  ${distro_id}            Installed origin.
  ${distro_codename}      Installed codename (eg, "jessie")

Codename based matching:
This will follow the migration of a release through different
archives (e. g. from testing to stable and later oldstable)::

     "o=Debian,n=jessie";
     "o=Debian,n=jessie-updates";
     "o=Debian,n=jessie-proposed-updates";
     "o=Debian,n=jessie,l=Debian-Security";

Archive or Suite based matching:
Note that this will silently match a different release after
migration to the specified archive (e. g. testing becomes the
new stable)::

     "o=Debian,a=stable";
     "o=Debian,a=stable-updates";
     "o=Debian,a=proposed-updates";
     "origin=Debian,codename=${distro_codename},label=Debian-Security";

Examples
~~~~~~~~

Include specified origin patterns for all hosts:

.. code-block:: yaml

   unattended_upgrades__origins:

     - origin: 'site=download.owncloud.org'

     - origin: [ 'site=download.example.org', 'o=Example Testing Packages' ]
       state: '{{ "present" if (ansible_hostname in [ "testing", "staging" ]) else "absent" }}'
