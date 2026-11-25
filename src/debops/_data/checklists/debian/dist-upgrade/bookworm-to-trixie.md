---
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later
title: "Debian 12 (bookworm) to 13 (trixie) release upgrade"
description: "Run a supervised bookworm -> trixie upgrade on a Debian host."
documentation:
  - https://www.debian.org/releases/trixie/release-notes/upgrading.en.html
  - https://www.debian.org/releases/trixie/release-notes/issues.en.html
  - https://debian-handbook.info/browse/stable/sect.dist-upgrade.html
---

# Debian 12 (bookworm) to 13 (trixie) release upgrade

This checklist tracks a supervised bookworm to trixie release upgrade.
It is bookkeeping, not the guide: the trixie release notes, chapters 4
and 5, are the authority -- when an item and the release notes disagree,
the release notes win.

Run the whole procedure in one `screen`/`tmux` session and commit a
checkpoint after each section. Skip-upgrades are not supported: start
from a fully updated bookworm with usrmerge completed. Items marked
"(if ...)" close as N/A where they do not apply.

Budget one to two hours of supervised wall-clock for a lean server,
more as the package count grows -- the APT run is download-bound (few
dozen minutes, Debian Handbook); prompts and service items stretch it.

| State   | Markers     | Meaning                    |
| ------- | ----------- | -------------------------- |
| open    | `[ ]`       | not done                   |
| done    | `[x]` `[X]` | resolved                   |
| blocked | `[B]` `[~]` | open, waiting on something |
| failed  | `[F]` `[!]` | resolved, unsuccessfully   |
| N/A     | `[N]` `[-]` | resolved                   |

Either marker spelling parses; unknown bracket content reads as open.

Task items are list lines: dash, asterisk and plus bullets and ordered
items (`1.`, `1)`) all parse, at any nesting depth; fenced code blocks
never carry items. Author with dash bullets as below -- the other
spellings exist so content pasted from elsewhere keeps its state.


## Preparation

- [ ] Confirm the host runs the latest bookworm point release
      (`cat /etc/debian_version`) and usrmerge is completed

- [ ] openssh-server at least 1:9.2p1-2+deb12u7 (bookworm stable-updates) --
      older versions can lock you out if the SSH session drops

- [ ] Replace DSA SSH keys with Ed25519 (`ssh -v` shows a
      "Server accepts key:" line) -- trixie dropped DSA support

- [ ] Confirm the architecture is still supported (i386 demoted to
      legacy; `mips*` gone; armel's last release)

- [ ] Skim the known severe bugs for ones matching this host
      (grub-efi-amd64 boot failures, kmod initramfs, linux boot hangs
      before the dmcrypt prompt)

- [ ] Back up what cannot be lost:
    - [ ] /etc
    - [ ] /var/lib/dpkg
    - [ ] /var/lib/apt/extended_states
    - [ ] `dpkg --get-selections '*'` output
    - [ ] (if aptitude) /var/lib/aptitude/pkgstates

- [ ] Verify the backup can actually be restored

- [ ] Back up user dotfiles (apps may overwrite settings on first
      start), or unmount /home for the duration

- [ ] Announce the maintenance window; a reboot will be required

- [ ] Plan for service downtime: replaced packages stop their services,
      an unattended prompt stretches it indefinitely

- [ ] For critical services plan the split: minimal upgrade ->
      kernel + reboot -> critical services -> full upgrade

- [ ] Confirm out-of-band access for recovery: serial console, iKVM or
      physical console; know the trixie installer rescue mode

- [ ] Review the recovery exits before you need them:
    - [ ] initrd debug shell -- initramfs-tools drops into it when the
          root fs cannot be mounted (`panic=0` disables it)
    - [ ] `systemd.unit=rescue.target` /
          `systemd.unit=emergency.target` (emergency:
          `mount -o remount,rw /` first)
    - [ ] `systemd.debug-shell=1` -- root shell on tty9, early in boot;
          disable after use

- [ ] Verify /boot is at least 768 MB with ~300 MB free (buster-or-older
      installs are likely too small -- grow the LV or drop old kernels)

- [ ] Run the upgrade inside `screen`/`tmux` (after a tmux
      major-version upgrade,
      `/proc/$(pgrep "tmux: server")/exe attach` reaches the old
      session)

- [ ] Note which VPN the host depends on (tinc) may drop mid-upgrade;
      do not rely on it for access

- [ ] (if micro-evtd watchdog) Stop the daemon and turn the watchdog
      off -- or it reboots the box mid-upgrade


## Start from pure bookworm

- [ ] Resolve pending actions in aptitude/synaptic, if used

- [ ] Remove obsolete packages (`apt list '?obsolete'`) -- unmaintained
      and they complicate the upgrade

- [ ] List packages not from Debian:
      `apt list '?narrow(?installed, ?not(?origin(Debian)))'` or
      `apt-forktracer | sort`

- [ ] Remove leftover config files from earlier upgrades:
      `find /etc -name '*.dpkg-*' -o -name '*.ucf-*' -o -name '*.merge-error'`

- [ ] (if non-free firmware) `non-free-firmware` present in APT sources

- [ ] Remove `proposed-updates` from the APT sources

- [ ] Remove bookworm-backports entries (regular backports upgrade
      cleanly but less tested; sloppy backports: no clean path)

- [ ] Point third-party archives at trixie builds or expect their
      packages removed during the upgrade

- [ ] Disable APT pinning holding packages off stable
      (/etc/apt/preferences, /etc/apt/preferences.d/)

- [ ] `dpkg --audit` -- resolve anything Half-Installed or Failed-Config

- [ ] `apt-mark showhold` -- release holds; re-hold local rebuilds
      deliberately

- [ ] Estimate space:
      `apt -o APT::Get::Trivial-Only=true full-upgrade` (may error
      early; re-run after the minimal upgrade)

- [ ] Free space if needed -- `apt clean`, `apt autoremove`, prune
      /var/log, drop unused locales (safest while sources still point
      at bookworm)


## Repoint APT sources at trixie

    Types: deb
    URIs: https://deb.debian.org/debian
    Suites: trixie trixie-updates
    Components: main non-free-firmware
    Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

    Types: deb
    URIs: https://security.debian.org/debian-security
    Suites: trixie-security
    Components: main non-free-firmware
    Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

- [ ] Write the deb822 sources above to
      /etc/apt/sources.list.d/debian.sources (adjust URI and
      components for a local mirror); remove the old
      /etc/apt/sources.list and `*.list` entries

- [ ] Verify nothing in `/etc/apt/sources.list*` references bookworm


## Service-specific pre-upgrade actions

- [ ] (if MariaDB) Clean shutdown first: `service mariadb stop`,
      confirm "Shutdown complete" in the log; if unclean, restart,
      let it recover, stop again

- [ ] (if RabbitMQ) Convert HA queues to quorum queues before the
      upgrade

- [ ] (if Dovecot) The 2.3 to 2.4 config format is incompatible --
      port in
      staging first; the replicator feature is gone

- [ ] (if bacula-director) Schema update needs ~2x database size plus
      a dump in /var/cache/dbconfig-common/backups; can run for hours
      or days

- [ ] (if plain-mode dm-crypt, non-LUKS) Record cipher, size and hash
      in /etc/crypttab -- bookworm defaults were
      `cipher=aes-cbc-essiv:sha256,size=256,hash=ripemd160`; trixie
      changed them and unrecorded devices read as random data

- [ ] (if legacy timezones like `US/*`) Find services that copied
      timezone names into config or data (PostgreSQL); tzdata-legacy
      provides the old names if needed


## Upgrade

apt logs package state changes to /var/log/apt/history.log and
term.log, dpkg to /var/log/dpkg.log -- the session records itself, and
term.log replays anything that scrolled off-screen. dpkg warnings
about "unable to delete old directory" come from the usrmerge
finalization and are safe to ignore.

- [ ] `apt update`

- [ ] Stop monitoring that restarts stopped services (monit)

- [ ] Minimal upgrade: `apt upgrade --without-new-pkgs` (no removals;
      read the apt-listchanges pager if shown)

- [ ] Ensure a kernel metapackage is installed:
      `dpkg -l 'linux-image*' | grep ^ii | grep -i meta`; if none,
      install the match for `uname -r` (usually linux-image-amd64)

- [ ] `apt full-upgrade` -- review proposed removals before confirming

- [ ] Resolve held-back packages: `apt list --upgradable` shows what
      stayed behind; `apt install <package>` moves them

- [ ] Handle apt failures if they occur -- mark this item [F] while
      broken, note the fix, resume:
    - "Could not perform immediate configuration" -> retry with
      `apt full-upgrade -o APT::Immediate-Configure=0`; if that
      fails, temporarily add the bookworm sources next to trixie
      and run `apt update`
    - Conflicts/Pre-Depends loop -> `-o APT::Force-LoopBreak=1` (an
      essential package is removed temporarily)
    - File conflict -> `dpkg -r --force-depends <package>` (named on the
      last error line), then repeat the upgrade
    - Dependency structure too corrupt -> `apt -f install`,
      `dpkg --configure --pending`, force-reinstall the offending .deb
      as a last resort

- [ ] Conffile prompts: answer "yes" for /etc/init.d scripts and
      /etc/manpath.config (old copies kept as .dpkg-old); note
      uncertain cases for later -- /var/log/apt/term.log remembers

- [ ] (if the console switches away mid-upgrade) Ctrl+Alt+F1 /
      Alt+F1 / Alt+arrow keys return to it


## Before reboot

The release notes say trixie needs no special pre-reboot actions; the
items below are the exceptions named elsewhere.

- [ ] (if users keep environment settings in ~/.pam_environment)
      openssh-server no longer reads it -- new logins lose them;
      migrate the settings now

- [ ] (if encrypted filesystems) verify systemd-cryptsetup installed

- [ ] (if arm64 cloud VM, UEFI)
      `touch /etc/grub.d/enable_cloud && apt install grub-cloud-arm64`

- [ ] (if RabbitMQ) Wipe /var/lib/rabbitmq/mnesia and restart the
      service -- no direct bookworm-to-trixie upgrade path

- [ ] (if Samba AD-DC) Install the samba-ad-dc package -- AD-DC split
      out of samba in trixie

- [ ] (if Samba with ceph or glusterfs VFS modules) Install
      samba-vfs-ceph / samba-vfs-glusterfs -- the modules split out
      of samba-vfs

- [ ] (if SSH GSSAPI authentication) Install openssh-client-gssapi
      and openssh-server-gssapi -- the GSSAPI support split out of
      the main packages

- [ ] Check for interface renames before rebooting:
    - [ ] `udevadm test-builtin net_setup_link /sys/class/net/<iface>`
          for each interface -- compare the reported `ID_NET_NAME`
    - [ ] If a rename would happen, pin the current names with a
          systemd.link file (triggers: i40e, `_SUN` ACPI object)


## Reboot and verify

A `System is tainted: unmerged-bin` notice during boot is expected;
leave it alone -- merging the directories manually is unsupported and
breaks future upgrades.

- [ ] Reboot into the new kernel (required)

- [ ] Host is back; recover via console if not

- [ ] Network interfaces kept their names; connectivity restored

- [ ] Critical services are up and serving

- [ ] Review what was removed or renamed (dpkg.log, apt history.log)


## Cleanup

- [ ] `apt autoremove` -- dependencies that changed with the release

- [ ] Review and purge obsolete packages: `apt list '?obsolete'` ->
      `apt purge '?obsolete'` (security support ends ~a year out)

- [ ] Purge removed packages' leftover configuration:
      `apt list '?config-files'` -> `apt purge '?config-files'`
      (purges their logs too -- back those up first)

- [ ] Remove transitional dummy packages that finished their job

- [ ] Finish the deb822 migration:
    - [ ] `apt modernize-sources`
    - [ ] Switch Signed-By keyring paths from .gpg to canonical .pgp --
          the .gpg symlinks will eventually disappear

- [ ] /etc/sysctl.conf is no longer read -- move local settings into
      `/etc/sysctl.d/*.conf`, then review
      /usr/lib/sysctl.d/50-default.conf (linux-sysctl-defaults)

- [ ] (if users ping) ping lost `CAP_NET_RAW`; verify unprivileged
      users can still ping (`ping_group_range`, shipped by
      linux-sysctl-defaults)

- [ ] /tmp is now a tmpfs (at most 50% of RAM), active after the reboot:
    - [ ] Relocate long-lived files or resize via
          `systemctl edit tmp.mount`
    - [ ] Old /tmp files are hidden after the switch --
          `mount --bind / /mnt` exposes them at /mnt/tmp

- [ ] /etc/tmpfiles.d/tmp.conf (from the upgrade) keeps the old /tmp
      and /var/tmp retention -- delete it to adopt the new defaults
      (10/30 days) or edit it

- [ ] (if you read login history) last, lastb and lastlog are gone --
      install wtmpdb + libpam-wtmpdb or lastlog2 + libpam-lastlog2,
      or clean up `/var/log/wtmp*`, `/var/log/lastlog*` and `/var/log/btmp*`

- [ ] (if libvirt) Verify the driver and storage packages you use
      survived the packaging split; check for obsolete conffiles
      (/usr/share/doc/libvirt-common/NEWS.Debian.gz)

- [ ] (if OpenLDAP) TLS moved from GnuTLS to OpenSSL -- review TLS
      options; the system default CA store loads when none configured

- [ ] (if strongSwan) Plan the charon to charon-systemd (swanctl)
      migration; the bookworm-era daemon keeps working while
      installed

- [ ] (if sg3-utils-udev) SCSI devices missed udev properties
      (bug 1109923, fixed in 1.48-3~deb13u1) -- verify device
      handling after the reboot anyway

- [ ] Review what forky will remove: sudo-ldap -> libsss-sudo, OpenSSH
      GSSAPI -> split packages, lxd -> incus, isc-dhcp (EOL),
      sudo_logsrvd (may be removed)


## Debrief

Done means: every item resolved -- done, failed, or N/A -- the host runs
trixie with services verified, and every change made by hand is
accounted for. There is no downgrade path: a broken upgrade is
repaired forward, or the host is restored from the backup taken in
Preparation.

- [ ] Codify every hand-made change -- APT sources, sysctl, tmpfiles,
      crypttab, interface pins, package holds -- into your
      configuration management before its next run

- [ ] Annotate the `[F]` and `[B]` items with what happened and how
      they resolved; the committed record is the post-mortem

- [ ] Schedule the follow-ups: deprecated-component migrations (the
      forky list above), EOL dates, the next upgrade

- [ ] Commit the final record to the vault and close the copy

Found a gap or an error in this checklist? Fix the source it was
opened from, not this copy.
