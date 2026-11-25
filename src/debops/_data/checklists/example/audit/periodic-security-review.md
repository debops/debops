---
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later
title: "Periodic security review"
description: "Recurring do-confirm security review of a Debian host."
documentation:
  - https://www.debian.org/security/
  - https://www.debian.org/security/faq
---

# Periodic security review

This is a do-confirm checklist: the host is supposed to already be in
good shape -- the configuration management maintains it -- and the
review verifies that nothing slipped. Deviations are findings, not
steps: mark them `[F]` and record the follow-up, do not fix them
mid-review.

One exception: evidence of an active intrusion -- an unknown key, an
unknown listener, unexplained processes, log gaps, successes right
after failure clusters -- is not a finding to schedule. Contain it
now: isolate the host, revoke the credentials, preserve the evidence,
hand the incident to your process; the record closes `[F]` with the
incident reference.

A finding's follow-up is a tracker reference or the configuration
management fix -- the next review verifies it happened. A per-host
re-review copy is the exception, not the default: open one under a
distinct id, scoped to the finding; `close --force` is legitimate for
a remediation copy.

Run it monthly on internet-facing hosts, quarterly on the rest. One
cycle is:

    debops checklist open review example/audit/periodic-security-review
    ... run the review, record findings and measured values ...
    debops checklist commit review --close

Each cycle commits its own dated record to the vault; the accumulated
records are the audit trail and the baseline the delta checks compare
against.

Budget 20-30 minutes per host: collection is minutes, investigation
scales with the findings. Plus the quarterly restore drill, unless
the cluster review's drill covers this host.

| State   | Markers     | Meaning                    |
| ------- | ----------- | -------------------------- |
| open    | `[ ]`       | not done                   |
| done    | `[x]` `[X]` | resolved                   |
| blocked | `[B]` `[~]` | open, waiting on something |
| failed  | `[F]` `[!]` | resolved, unsuccessfully   |
| N/A     | `[N]` `[-]` | resolved                   |

Either marker spelling parses; unknown bracket content reads as open.
A `[F]` here means a deviation was found and recorded, not that a fix
was attempted and failed.

## Backups

- [ ] Verify the most recent backup job completed successfully and the
      destination has capacity

- [ ] Restore a file or a small set from the latest backup (the
      cluster review's quarterly drill may cover this host)

## Updates

- [ ] Check for unapplied updates: `apt update && apt list
      --upgradable` -- security updates pending are findings, not
      chores

- [ ] Run `debsecan` -- Debian security advisories since the last
      review are answered on this host

- [ ] (if unattended upgrades) Verify recent automatic runs in
      /var/log/unattended-upgrades/

- [ ] Check held packages: `apt-mark showhold` -- every hold still has
      a reason

- [ ] Check obsolete packages: `apt list '?obsolete'` -- compare
      against the last cycle's record; old kernels appear here by
      design, `apt autoremove` handles them

## Certificates

- [ ] (if public TLS) Verify exposed certificates have more than one
      review cycle plus two weeks left

- [ ] (if internal PKI) Verify this host's certificates renewed on
      schedule

## Access

- [ ] Review `authorized_keys` entries -- each key maps to a person or
      role that should still hold it

- [ ] Verify only root holds UID 0, and interactive shells belong to
      declared users

- [ ] Review sudo use since the last review (journal and sudo logs)

- [ ] (if accounts changed) Verify departed users lost all access:
      account gone or locked, and no residual keys, cron entries,
      sudo grants or login history under the old name

## Services

- [ ] Run `ss -tulpn` -- every listening address and service maps to a
      declared service; anything else is a finding

- [ ] `systemctl --failed` is empty

- [ ] `systemctl list-timers --all` -- the unattended-upgrades,
      certificate and backup timers show a recent, successful last
      trigger

## Integrity

- [ ] Run `debsums -s` (configuration excluded) -- no replaced system
      files

- [ ] Compare the SUID/SGID inventory (`find / -xdev -perm /6000`)
      against the last cycle's record -- new entries are findings

- [ ] (if AppArmor) `aa-status` -- profiles loaded, none disabled

## Logs and alarms

- [ ] Compare authentication failure counts against the last cycle's
      record; investigate successes right after failure clusters and
      failures for unknown users

## System state

- [ ] Verify the running kernel is the newest installed one (`uname
      -r` against `dpkg -l 'linux-image*'`) -- a pending reboot
      leaves the fix unrunning

- [ ] Verify free space did not drop notably since the last review
      (`df -h` and `df -i`), and /boot has at least ~200 MB free

- [ ] Verify time sync is healthy (`timedatectl` or `chronyc
      tracking`)

- [ ] Check `dpkg --audit` -- nothing Half-Installed or Failed-Config

- [ ] Run configuration management in check mode (`debops check`) and
      account for every unexpected change -- an unexplained change is
      compromise, not drift. Check mode runs tasks marked
      `check_mode: False` for real; DebOps roles confine those to
      fact gathering

- [ ] Verify configuration management ran within its window since the
      last review

## Findings and debrief

Done means every check ticked -- pass, failed, or N/A -- and every
`[F]` item annotated with the finding and where its follow-up lives.
Record the measured values with the ticks -- failure counts,
obsolete-package count, minimum certificate days, free space per
filesystem -- so the next cycle's delta checks compare against
numbers, not memory. The committed record should answer, a year from
now, what was checked, what was found, and what was done about it.

- [ ] Verify every finding from the previous record is resolved or
      rescheduled

- [ ] Record each `[F]` finding with its follow-up (tracker reference
      or the fix)

- [ ] Schedule the next review

- [ ] Commit the record to the vault and close the copy

Found a gap or an error in this checklist? Fix the source it was
opened from, not this copy.
