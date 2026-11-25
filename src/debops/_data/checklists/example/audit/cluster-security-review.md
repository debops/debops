---
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later
title: "Cluster security review"
description: "Recurring do-confirm security review of a DebOps cluster."
documentation:
  - https://www.debian.org/security/
  - https://www.debian.org/security/faq
---

# Cluster security review

Do-confirm, run from the controller against the whole inventory.
Where the per-host review (`example/audit/periodic-security-review`)
inspects, this one queries: every item is one batch command over the
inventory with your usual ad-hoc mechanism, and a finding names the
hosts that need hands-on work. A finding's follow-up is a tracker
reference or the configuration management fix -- the next cycle's
query verifies it happened. A per-host copy of the host review is the
exception, not the default: open one under a distinct id
(`web1/recheck`), scoped to the finding; `close --force` is
legitimate for a remediation copy.

One exception to the recording discipline: evidence of an active
intrusion -- unknown keys, unknown listeners, log gaps, successes
right after failure clusters -- is contained immediately: isolate the
hosts, revoke the credentials, preserve the evidence, hand the
incident to your process. The record closes `[F]` with the incident
reference.

Run it monthly on internet-facing clusters, quarterly on the rest.
One cycle is:

    debops checklist open cluster example/audit/cluster-security-review
    ... run the batch queries, record findings and measured values ...
    debops checklist commit cluster --close

Budget 60-90 minutes of wall-clock on a month with findings, less on
a clean one: collection is independent of host count, investigation
is not.

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

## Inventory

- [ ] Account for every host: each one answered the batch queries --
      unreachable is a finding, not a smaller checklist

- [ ] (each quarter) Sweep the network for hosts that answer but are
      not in the inventory -- shadow hosts are outside every other
      check by definition

- [ ] (if monitoring) Verify every inventory host is monitored, and no
      alert is silenced without a reason and an expiry

## Backups

- [ ] Verify every host's latest backup job succeeded (backup
      reports), the destination has capacity, and the backups are
      encrypted with one copy offline or immutable -- expect: no
      failures

- [ ] (each quarter) Full restore drill, round-robin: each quarter's
      host comes from the rotation, so the vault shows the coverage

## Updates

- [ ] Check the inventory for hosts with unapplied security updates
      (`apt update && apt list --upgradable`) -- expect: none; a
      finding lists the hosts

- [ ] Run `debsecan` over the inventory -- Debian security advisories
      since the last review are answered on every affected host

- [ ] Check for hosts carrying obsolete packages -- expect: none, or
      a recorded plan

- [ ] Verify every host runs a supported release
      (`cat /etc/debian_version`) -- a forgotten EOL host hides from
      every other check

- [ ] Verify the running kernel is the newest installed one on every
      host -- unattended upgrades install kernels and do not reboot;
      a pending reboot leaves the fix unrunning

## Certificates

- [ ] Verify every exposed endpoint's certificate has more than one
      review cycle plus two weeks left -- one query over the
      inventory

## Access

- [ ] Sweep every `authorized_keys` on every host -- each key maps to
      a person or role that should still hold it; keys outside the
      managed paths are findings on their own

- [ ] Verify departed users lost all access: accounts against the
      declared list, and no residual keys, cron entries, sudo grants
      or recent logins under departed names

## Services

- [ ] Verify no host listens beyond its declared services
      (`ss -tulpn` over the inventory) -- an unexpected listener is
      the one thing check mode cannot see

- [ ] Verify failed units and timers across the inventory
      (`systemctl --failed`, `systemctl list-timers --all`) -- the
      unattended-upgrades, certificate and backup timers show recent,
      successful last triggers

## Logs

- [ ] Check authentication failure counts against the last cycle's
      record; investigate successes right after failure clusters

- [ ] Verify every host's newest log line reached the aggregation
      point recently -- a broken shipper and a suppressed log stream
      look the same from inside the host

## System state

- [ ] Run configuration management in check mode across the inventory
      (`debops check`) and account for every unexpected change -- an
      unexplained change is compromise, not drift. Check mode runs
      tasks marked `check_mode: False` for real; DebOps roles confine
      those to fact gathering

- [ ] Verify free space did not drop notably since the last review
      (`df -h` and `df -i`)

- [ ] Verify time sync is healthy across the inventory (`timedatectl`
      or `chronyc tracking`)

## Findings and debrief

Done means every check ticked -- pass, failed, or N/A -- and every
`[F]` item annotated with its finding: which hosts, what the
deviation is, where the follow-up lives. Record the measured values
with the ticks -- failure counts, hosts with pending updates,
minimum certificate days -- so the next cycle compares against
numbers. The remediation trail lives in the tracker or the
configuration management repository; this record should answer, a
year from now, what was checked across the cluster and what was
found.

- [ ] Verify every finding from the previous record is resolved or
      rescheduled

- [ ] Record each `[F]` finding with the affected hosts and the
      follow-up (tracker reference or the fix)

- [ ] Schedule the next review

- [ ] Commit the record to the vault and close the copy

Found a gap or an error in this checklist? Fix the source it was
opened from, not this copy.
