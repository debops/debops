#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2014, Ilya Barsukov <barsukov@selectel.ru>, Selectel LLC
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# import module snippets
from ansible.module_utils.basic import *
import os


DOCUMENTATION = """
---
module: btrfs_subvolume
short_description: Provides `create` and `delete` subvolumes methods.
description:
     - The M(btrfs_subvolume) module takes the command name followed by
       a list of space-delimited arguments.
     - The given command will be executed on all selected nodes.
version_added: 0.1
author: Ilya Barsukov
options:
    state:
        description:
            - creates or deletes subvolume
        required: true
        choices: ["present", "absent"]
    path:
        description:
            - subvolume absolute path
        required: true
        default: null
    qgroups:
        required: false
        description:
            - list of qgroup ids, adds the newly created subvolume to a qgroup
        default: []
    commit:
        required: false
        description:
            - wait for transaction commit at the end of the operation
              or of the each
        choices: ["each", "after", "no"]
        default: "no"
    recursive:
        required: false
        choices: [true, false]
        description:
            - create or delete subvolumes recursively
        default: false
"""

EXAMPLES = """
# Example for Ansible Playbooks.
- name: Recursive create given subvolume path
  btrfs_subvolume:
    state: 'present'
    path: '/storage/test/test1/test2'
    qgroups:
      - '1/100'
      - '1/101'
    recursive: True

- name: Delete given Btrfs subvolume
  btrfs_subvolume:
    state: 'absent'
    path: '/storage/test/test1/test2'
    commit: 'each'
"""


def get_subvolumes(path, subs=None):
    if subs is None:
        subs = []
    subvolumes = os.listdir(path)
    for sub in subvolumes:
        sub = os.path.sep.join([path, sub])

        if not os.path.isdir(sub):
            continue

        subs.append(sub)
        subs = get_subvolumes(sub, subs=subs)

    return subs


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, choices=['present', 'absent'],
                       type='str'),
            path=dict(required=True, default=None, type='str'),
            qgroups=dict(default=[], type='list'),
            commit=dict(default='no', choices=['after', 'each', 'no'],
                        type='str'),
            recursive=dict(default='False', type='bool')
        ),
        supports_check_mode=True
    )
    result = {
        'changed': False,
        'commands': [],
        'check': module.check_mode
    }
    param_path = module.params['path'].rstrip(os.path.sep)

    if module.params['state'] == 'present':
        # Creating subvolume
        if not os.path.exists(param_path) and not module.params['recursive']:
            cmd = 'btrfs subvolume create {qgroups} {subvolume}'.format(
                qgroups=' -i '.join(['']+module.params['qgroups']),
                subvolume=param_path,
            )
            result['commands'].append(cmd)
            if not module.check_mode:
                module.run_command(cmd, check_rc=True)
                result['changed'] = True

        elif module.params['recursive']:
            # Check parent subvolumes and create it if they doesnt exist
            parents = param_path.split(os.path.sep)
            for idx, subvolume in enumerate(parents):
                if len(subvolume) == 0:
                    continue

                subvolume = os.path.sep.join(parents[:idx+1])

                if not os.path.exists(subvolume):
                    cmd = ('btrfs subvolume create '
                           '{qgroups} {subvolume}').format(
                        qgroups=' -i '.join(['']+module.params['qgroups']),
                        subvolume=subvolume,
                    )

                    result['commands'].append(cmd)
                    if not module.check_mode:
                        module.run_command(cmd, check_rc=True)
                        result['changed'] = True

    elif module.params['state'] == 'absent':
        # Delete subvolume
        commit = ''
        if module.params['commit'] != 'no':
            commit = '--commit-{}'.format(module.params['commit'])

        if os.path.exists(param_path):
            if not module.params['recursive']:
                cmd = 'btrfs subvolume delete {commit} {subvolume}'.format(
                    commit=commit, subvolume=param_path
                )
                result['commands'].append(cmd)
                if not module.check_mode:
                    module.run_command(cmd, check_rc=True)
                    result['changed'] = True

            elif module.params['recursive']:
                # reversed parent directories from end to beginning
                subvolumes = get_subvolumes(param_path)
                subvolumes.insert(0, param_path)

                for sub in reversed(subvolumes):

                    if os.path.exists(sub):
                        cmd = ('btrfs subvolume delete '
                               '{commit} {subvolume}').format(
                            commit=commit, subvolume=sub
                        )

                        result['commands'].append(cmd)
                        if not module.check_mode:
                            module.run_command(cmd, check_rc=True)
                            result['changed'] = True

    if module.check_mode and result['commands']:
        result['changed'] = True

    if not module.check_mode:
        del result['check']

    if not result['commands']:
        del result['commands']

    module.exit_json(**result)


if __name__ == '__main__':
    main()
