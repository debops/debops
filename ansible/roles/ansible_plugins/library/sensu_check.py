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
module: sensu_check
author:
  - Paul Arthur (@flowerysong)
  - Aljaz Kosir (@aljazkosir)
  - Miha Plesko (@miha-plesko)
  - Tadej Borovsak (@tadeboro)
short_description: Manage Sensu checks
description:
  - Create, update or delete Sensu Go check.
  - For more information, refer to the Sensu Go documentation at
    U(https://docs.sensu.io/sensu-go/latest/reference/checks/).
version_added: "1.0"
extends_documentation_fragment:
  - sensu.sensu_go.auth
  - sensu.sensu_go.name
  - sensu.sensu_go.namespace
  - sensu.sensu_go.state
  - sensu.sensu_go.labels
  - sensu.sensu_go.annotations
options:
  command:
    description:
      - Check command to run.
      - Required if I(state) is C(present).
    type: str
    required: true
  subscriptions:
    description:
      - List of subscriptions which receive check requests.
      - Required if I(state) is C(present).
    type: list
  handlers:
    description:
      - List of handlers which receive check results.
    type: list
  interval:
    description:
      - Check request interval.
      - Cannot be used when I(cron) option is used.
    type: int
  cron:
    description:
      - Schedule check requests using crontab syntax.
      - Cannot be used when I(interval) option is used.
    type: str
  publish:
    description:
      - Enables or disables scheduled publication of check requests.
    type: bool
  timeout:
    description:
      - Check execution timeout.
    type: int
  ttl:
    description:
      - Amount of time after which a check result is considered stale.
    type: int
  stdin:
    description:
      - Enables writing of serialized JSON data to the check command's stdin.
      - Only usable with checks written specifically for Sensu Go.
    type: bool
  low_flap_threshold:
    description:
      - Low flap threshold.
    type: int
  high_flap_threshold:
    description:
      - High flap threshold.
    type: int
  runtime_assets:
    description:
      - List of runtime assets required to run the check.
    type: list
  check_hooks:
    description:
      - A mapping of response codes to hooks which will be run by the agent when that code is returned.
    type: dict
  proxy_entity_name:
    description:
      - Entity name to associate this check with instead of the agent it ran on.
    type: str
  proxy_requests:
    description:
      - Allows you to assign the check to run for multiple entities according
        to their entity_attributes.
    type: dict
    suboptions:
      entity_attributes:
        description:
          - List of attribute checks for determining which proxy entities this check should be scheduled against.
        type: list
      splay:
        description:
          - Enables or disables splaying of check request scheduling.
        type: bool
      splay_coverage:
        description:
          - Percentage of the C(interval) over which to splay checks.
        type: int
  output_metric_format:
    description:
      - Enable parsing of metrics in the specified format from this check's
        output.
    type: str
    choices:
      - graphite_plaintext
      - influxdb_line
      - nagios_perfdata
      - opentsdb_line
  output_metric_handlers:
    description:
      - List of handlers which receive check results.
    type: list
  round_robin:
    description:
      -  When set to true, Sensu executes the check once per interval, cycling through each subscribing agent in turn.
    type: bool
  env_vars:
    description:
      - A mapping of environment variable names and values to use with command execution.
    type: dict
'''

EXAMPLES = '''
- name: Check executing command every 30 seconds
  sensu_check:
    name: check
    command: check-cpu.sh -w 75 -c 90
    subscriptions:
      - checks
    interval: 30
    publish: yes

- name: Check executing command with cron scheduler
  sensu_check:
    name: check
    command: check-cpu.sh -w 75 -c 90
    subscriptions:
      - systems
    handlers:
      - slack
    cron: "* * * * *"
    publish: yes

- name: Ad-hoc scheduling
  sensu_check:
    name: check
    command: check-cpu.sh -w 75 -c 90
    subscriptions:
      - systems
    handlers:
      - slack
    interval: 60
    publish: no

- name: Report events under proxy entity name instead of agent entity
  sensu_check:
    name: check
    command: http_check.sh https://sensu.io
    subscriptions:
      - proxy
    handlers:
      - slack
    interval: 60
    proxy_entity_name: sensu-site
    round_robin: yes
    publish: yes

- name: Remove check
  sensu_check:
    name: my-check
    state: absent
'''

RETURN = '''
object:
    description: object representing Sensu check
    returned: success
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.sensu import (
    arguments, errors, utils
)


def validate_module_params(module):
    params = module.params
    proxy_requests = params['proxy_requests']

    if (proxy_requests and proxy_requests.get('splay', False) and
            proxy_requests.get('splay_coverage') is None):
        module.fail_json(msg='splay is true but all of the following are missing: splay_coverage')

    if params['state'] == 'present' and not (params['interval'] or params['cron']):
        module.fail_json(msg='one of the following is required: interval, cron')


def build_api_payload(params):
    payload = arguments.get_mutation_payload(
        params,
        'command',
        'cron',
        'handlers',
        'high_flap_threshold',
        'interval',
        'low_flap_threshold',
        'output_metric_format',
        'output_metric_handlers',
        'proxy_entity_name',
        'proxy_requests',
        'publish',
        'round_robin',
        'runtime_assets',
        'stdin',
        'subscriptions',
        'timeout',
        'ttl'
    )
    if params['check_hooks']:
        payload['check_hooks'] = utils.dict_to_single_item_dicts(params['check_hooks'])

    if params['env_vars']:
        payload['env_vars'] = utils.dict_to_key_value_strings(params['env_vars'])

    return payload


def main():
    required_if = [
        ('state', 'present', ['subscriptions', 'command'])
    ]
    mutually_exclusive = [('interval', 'cron')]

    module = AnsibleModule(
        supports_check_mode=True,
        required_if=required_if,
        mutually_exclusive=mutually_exclusive,
        argument_spec=dict(
            arguments.get_spec(
                "auth", "name", "state", "labels", "annotations", "namespace",
            ),
            command=dict(),
            subscriptions=dict(
                type='list'
            ),
            handlers=dict(
                type='list'
            ),
            interval=dict(
                type='int'
            ),
            cron=dict(),
            publish=dict(
                type='bool'
            ),
            timeout=dict(
                type='int'
            ),
            ttl=dict(
                type='int'
            ),
            stdin=dict(
                type='bool'
            ),
            env_vars=dict(
                type='dict'
            ),
            low_flap_threshold=dict(
                type='int'
            ),
            high_flap_threshold=dict(
                type='int'
            ),
            runtime_assets=dict(
                type='list'
            ),
            check_hooks=dict(
                type='dict'
            ),
            proxy_entity_name=dict(),
            proxy_requests=dict(
                type='dict',
                options=dict(
                    entity_attributes=dict(
                        type='list'
                    ),
                    splay=dict(
                        type='bool'
                    ),
                    splay_coverage=dict(
                        type='int'
                    )
                )
            ),
            output_metric_format=dict(
                choices=['nagios_perfdata', 'graphite_plaintext', 'influxdb_line', 'opentsdb_line']
            ),
            output_metric_handlers=dict(
                type='list'
            ),
            round_robin=dict(
                type='bool'
            )
        )
    )
    validate_module_params(module)
    client = arguments.get_sensu_client(module.params['auth'])
    path = utils.build_core_v2_path(
        module.params['namespace'], 'checks', module.params['name'],
    )
    payload = build_api_payload(module.params)

    try:
        changed, check = utils.sync(
            module.params['state'], client, path, payload, module.check_mode,
        )
        module.exit_json(changed=changed, object=check)
    except errors.Error as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
