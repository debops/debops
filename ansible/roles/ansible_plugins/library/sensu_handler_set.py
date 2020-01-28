#!/usr/bin/python
# -*- coding: utf-8 -*-
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
module: sensu_handler_set
author:
  - Aljaz Kosir (@aljazkosir)
  - Miha Plesko (@miha-plesko)
  - Tadej Borovsak (@tadeboro)
short_description: Manage Sensu handler set
description:
  - Create, update or delete Sensu handler set.
  - For more information, refer to the Sensu documentation at
    U(https://docs.sensu.io/sensu-go/latest/reference/handlers/#handler-sets).
version_added: "1.0"
extends_documentation_fragment:
  - sensu.auth
  - sensu.name
  - sensu.namespace
  - sensu.state
  - sensu.labels
  - sensu.annotations
options:
  handlers:
    description:
      - List of Sensu event handlers (names) to use for events using the handler set.
      - Required if I(state) is C(present).
    type: list
'''

EXAMPLES = '''
- name: Create a handler set
  sensu_handler_set:
    name: notify_all_the_things
    handlers:
      - slack
      - tcp_handler
      - udp_handler

- name: Delete a handler set
  sensu_handler_set:
    name: notify_all_the_things
    state: absent
'''

RETURN = '''
object:
    description: object representing Sensu handler set
    returned: success
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.sensu import (
    arguments, errors, utils,
)


def main():
    required_if = [
        ('state', 'present', ['handlers'])
    ]
    module = AnsibleModule(
        supports_check_mode=True,
        required_if=required_if,
        argument_spec=dict(
            arguments.get_spec(
                "auth", "name", "state", "labels", "annotations", "namespace",
            ),
            handlers=dict(
                type='list'
            ),
        ),
    )

    client = arguments.get_sensu_client(module.params['auth'])
    path = utils.build_core_v2_path(
        module.params['namespace'], 'handlers', module.params['name'],
    )
    payload = arguments.get_mutation_payload(
        module.params, 'handlers'
    )
    payload['type'] = 'set'

    try:
        changed, handler = utils.sync(
            module.params['state'], client, path, payload, module.check_mode,
        )
        module.exit_json(changed=changed, object=handler)
    except errors.Error as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
