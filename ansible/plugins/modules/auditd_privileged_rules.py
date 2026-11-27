# .. Copyright (C) 2026-2027 seven-beep <github@soulintheshell.com>
# .. SPDX-License-Identifier: GPL-3.0-or-later

import io
import json
import os
import subprocess

from ansible.module_utils.basic import AnsibleModule

DEFAULT_MAX_SCAN_SIZE = 1099511627776  # 1 TiB

DOCUMENTATION = r'''
---
module: privileged_file_audit
short_description: Find privileged files and generate an audit rule recommendation
description:
  - Scans selected directories or eligible mounted filesystems for regular files
    with setuid or setgid permission bits.
  - Returns a rule recommendation for collecting audit events related to the
    discovered files. It does not install or apply the rule.
  - Always reports C(changed=false); check mode is supported.
options:
  max_scan_size:
    description:
      - Maximum size, in bytes, of any filesystem scanned during automatic
        filesystem discovery.
      - Has no effect when C(targets) is supplied.
      - Set to C(0) to disable the size limit.
    type: int
    default: 536870912000
  uid_min:
    description:
      - Minimum audit user ID included in the generated rule's C(auid) filter.
    type: int
    default: 1000
  targets:
    description:
      - Directories to scan instead of discovering mounted filesystems.
      - Each path must be an existing directory. When supplied, filesystem
        discovery, mount-option exclusions, and C(max_scan_size) checks are
        bypassed.
    type: list
    elements: path
    default: null
  exclude_mount_options:
    description:
      - Mount options that disqualify a filesystem during automatic discovery.
      - Filesystems whose type is marked C(nodev) in C(/proc/filesystems) are
        also excluded.
      - Ignored when C(targets) is supplied.
    type: list
    elements: str
    default:
      - noexec
      - nosuid
requirements:
  - findmnt
  - find
author:
  - (@seven-beep)
'''


def nodev_filesystem_types():
    """Return filesystem types marked nodev in /proc/filesystems."""
    result = set()
    with io.open("/proc/filesystems", "r", encoding="utf-8") as proc_fs:
        for line in proc_fs:
            fields = line.split()
            if len(fields) == 2 and fields[0] == "nodev":
                result.add(fields[1])
    return result


def discover_filesystems(exclude_mount_options):
    command = [
        "findmnt",
        "--noheadings",
        "--kernel",
        "--json",
        "--df",
        "--bytes",
        "--output",
        "fstype,size,target,options",
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode, command, output=stdout, stderr=stderr
        )

    filesystems = json.loads(stdout).get("filesystems", [])

    nodev_types = nodev_filesystem_types()
    eligible = []

    for fs in filesystems:
        options = set(fs.get("options", "").split(","))
        if fs.get("fstype") in nodev_types:
            continue
        if options.intersection(exclude_mount_options):
            continue
        eligible.append(fs)

    return eligible


def find_privileged_files(target):
    # Use NUL delimiters so spaces in paths are preserved.
    command = [
        "find",
        target,
        "-xdev",
        "-perm",
        "/6000",
        "-type",
        "f",
        "-print0",
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode, command, output=stdout, stderr=stderr
        )

    return [path.decode("utf-8", "replace") for path in stdout.split(b"\0") if path]


def make_debops_rules(paths, uid_min):
    if not paths:
        return []

    return [
        {
            "name": "Ensure use of privileged commands are collected",
            "fields": [
                "arch=b64",
                "perm=x",
                "auid>={}".format(uid_min),
                "auid!=unset",
            ],
            "syscalls": ["all"],
            "keys": ["privileged"],
            "paths": paths,
            "state": "present",
        }
    ]


def main():
    module = AnsibleModule(
        argument_spec={
            "max_scan_size": {
                "type": "int",
                "default": DEFAULT_MAX_SCAN_SIZE,
            },
            "uid_min": {
                "type": "int",
                "default": 1000,
            },
            "targets": {
                "type": "list",
                "elements": "path",
                "default": None,
            },
            "exclude_mount_options": {
                "type": "list",
                "elements": "str",
                "default": ["noexec", "nosuid"],
            },
        },
        supports_check_mode=True,
    )

    params = module.params
    max_scan_size = params["max_scan_size"]
    uid_min = params["uid_min"]

    if max_scan_size < 0:
        module.fail_json(msg="max_scan_size must be 0 or greater")
    if uid_min < 0:
        module.fail_json(msg="uid_min must be 0 or greater")

    try:
        if params["targets"] is not None:
            targets = params["targets"]
            for target in targets:
                if not os.path.isdir(target):
                    module.fail_json(msg="Target is not a directory: {}".format(target))
            filesystems = []
        else:
            filesystems = discover_filesystems(
                params["exclude_mount_options"],
            )
            targets = [fs["target"] for fs in filesystems]

            if max_scan_size > 0:
                oversized = [
                    fs for fs in filesystems if int(fs["size"]) > max_scan_size
                ]
                if oversized:
                    module.fail_json(
                        msg="One or more filesystems exceed max_scan_size",
                        oversized_filesystems=[
                            {
                                "target": fs["target"],
                                "size_bytes": int(fs["size"]),
                            }
                            for fs in oversized
                        ],
                    )

        privileged_paths = []
        for target in targets:
            privileged_paths.extend(find_privileged_files(target))

        # Deduplicate while retaining scan order.
        privileged_paths = list(dict.fromkeys(privileged_paths))

        generated_rules = make_debops_rules(privileged_paths, uid_min)
        output_data = [
            {
                "name": "50-privileged",
                "comment": (
                    "Recommendations from the CIS benchmarks.\n"
                    "https://www.cisecurity.org/cis-benchmarks"
                ),
                "check_path": False,
                "rules": generated_rules,
                "state": "present",
            }
        ]

        module.exit_json(
            changed=False,
            data=output_data,
            scanned_targets=targets,
            privileged_paths=privileged_paths,
            filesystem_count=len(filesystems),
            file_count=len(privileged_paths),
        )

    except subprocess.CalledProcessError as exc:
        # Handle potential None types for stdout/stderr in Py2
        stderr_val = exc.stderr if exc.stderr else ""
        if isinstance(stderr_val, bytes):
            stderr_val = stderr_val.decode("utf-8", "replace")

        module.fail_json(
            msg="A filesystem discovery or find command failed",
            command=exc.cmd,
            returncode=exc.returncode,
            stderr=stderr_val,
        )
    except (OSError, ValueError, KeyError) as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
