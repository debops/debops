#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Paul Arthur <paul.arthur@flowerysong.com>
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["stableinterface"],
    "supported_by": "certified",
}

DOCUMENTATION = '''
module: sensu_user
author:
  - Paul Arthur (@flowerysong)
  - Aljaz Kosir (@aljazkosir)
  - Tadej Borovsak (@tadeboro)
short_description: Manage Sensu users
description:
  - Create, update, activate or deactivate Sensu user.
  - For more information, refer to the Sensu documentation at
    U(https://docs.sensu.io/sensu-go/latest/reference/rbac/#users).
version_added: "1.0"
extends_documentation_fragment:
  - sensu.auth
  - sensu.name
options:
  state:
    description:
      - Desired state of the user.
      - Users cannot actually be deleted, only deactivated.
    type: str
    choices: [ enabled, disabled ]
    default: enabled
  password:
    description:
      - Password for the user.
      - Required if I(state) is C(enabled).
    type: str
  groups:
    description:
      - List of groups user belongs to.
    type: list
'''

EXAMPLES = '''
- name: Create a user
  sensu_user:
    auth:
      url: http://localhost:8080
    name: awesome_username
    password: hidden_password?
    groups:
      - dev
      - prod

- name: Deactivate a user
  sensu_user:
    name: awesome_username
    state: absent
'''

RETURN = '''
object:
    description: object representing Sensu user
    returned: success
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.sensu import (
    arguments, errors, utils,
)


def sync(remote_object, state, client, path, payload, check_mode):
    if state == 'absent' and remote_object is not None:
        if not check_mode:
            utils.delete(client, path)
        return True, utils.get(client, path)

    if utils.do_differ(remote_object, payload):
        if check_mode:
            return True, payload
        utils.put(client, path, payload)
        return True, utils.get(client, path)

    return False, remote_object


def main():
    required_if = [
        ('state', 'present', ('password', ))
    ]
    module = AnsibleModule(
        required_if=required_if,
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("auth", "name"),
            state=dict(
                default='present',
                choices=['present', 'absent'],
            ),
            password=dict(
                no_log=True
            ),
            groups=dict(
                type='list',
            )
        ),
    )

    client = arguments.get_sensu_client(module.params['auth'])
    path = utils.build_core_v2_path(None, 'users', module.params['name'])
    state = module.params['state']

    try:
        remote_object = utils.get(client, path)
    except errors.Error as e:
        module.fail_json(msg=str(e))

    if remote_object is None and state == 'absent' and module.params['password'] is None:
        module.fail_json(msg='Cannot disable a non existent user')

    payload = arguments.get_spec_payload(module.params, 'password', 'groups')
    payload['username'] = module.params['name']
    payload['disabled'] = module.params['state'] == 'absent'

    try:
        changed, user = sync(
            remote_object, state, client, path, payload, module.check_mode
        )
        module.exit_json(changed=changed, object=user)
    except errors.Error as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
