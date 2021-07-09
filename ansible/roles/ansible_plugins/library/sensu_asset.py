#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Cameron Hurst <cahurst@cisco.com>
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

DOCUMENTATION = """
module: sensu_asset
author:
  - Cameron Hurst (@wakemaster39)
  - Aljaz Kosir (@aljazkosir)
  - Manca Bizjak (@mancabizjak)
  - Miha Plesko (@miha-plesko)
  - Tadej Borovsak (@tadeboro)
short_description: Manage Sensu assets
description:
  - Create, update or delete Sensu Go asset.
  - For more information, refer to the Sensu documentation at
    U(https://docs.sensu.io/sensu-go/latest/reference/assets/).
version_added: "1.0"
extends_documentation_fragment:
  - sensu.auth
  - sensu.name
  - sensu.namespace
  - sensu.state
  - sensu.labels
  - sensu.annotations
options:
  builds:
    description:
      - A list of asset builds used to define multiple artefacts which
        provide the named asset.
      - Required if I(state) is C(present).
    type: list
    suboptions:
      url:
        description:
          - The URL location of the asset.
        type: str
        required: yes
      sha512:
        description:
          - The checksum of the asset.
        type: str
        required: yes
      filters:
        description:
          - A set of Sensu query expressions used to determine if the asset
            should be installed.
        type: list
      headers:
        description:
          - Additional headers to send when retrieving the asset, e.g. for
            authorization.
        type: dict
"""

EXAMPLES = """
- name: Create a multiple-build asset
  sensu_asset:
    name: sensu-plugins-cpu-checks
    builds:
      - url: https://assets.bonsai.sensu.io/68546e739d96fd695655b77b35b5aabfbabeb056/sensu-plugins-cpu-checks_4.0.0_centos_linux_amd64.tar.gz
        sha512: 518e7c17cf670393045bff4af318e1d35955bfde166e9ceec2b469109252f79043ed133241c4dc96501b6636a1ec5e008ea9ce055d1609865635d4f004d7187b
        filters:
          - entity.system.os == 'linux'
          - entity.system.arch == 'amd64'
          - entity.system.platform == 'rhel'
      - url: https://assets.bonsai.sensu.io/68546e739d96fd695655b77b35b5aabfbabeb056/sensu-plugins-cpu-checks_4.0.0_alpine_linux_amd64.tar.gz
        sha512: b2da25ecd7642e6de41fde37d674fe19dcb6ee3d680e145e32289f7cfc352e6b5f9413ee9b701d61faeaa47b399aa30b25885dbc1ca432c4061c8823774c28f3
        filters:
          - entity.system.os == 'linux'
          - entity.system.arch == 'amd64'
          - entity.system.platform == 'alpine'

- name: Delete an asset
  sensu_asset:
    name: sensu-plugins-cpu-check
    state: absent
"""

RETURN = """
object:
    description: object representing Sensu asset
    returned: success
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.sensu import (
    arguments, errors, utils,
)


def validate_module_params(params):
    if params["state"] == "present":
        if not params['builds']:
            return "builds must include at least one element"
    return None


def _build_set(builds):
    return {(
        b.get('sha512'),
        b.get('url'),
        frozenset((b.get('headers', {}) or {}).items()),
        frozenset(b.get('filters', []) or []),
    ) for b in builds}


def _do_builds_differ(current, desired):
    if len(current) != len(desired):
        return True

    return _build_set(current) != _build_set(desired)


def do_differ(current, desired):
    if current is None:
        return True

    for key, value in desired.items():
        current_value = current.get(key)
        if key == 'builds':
            if _do_builds_differ(current_value, value):
                return True
        elif value != current_value:
            return True
    return False


def build_api_payload(params):
    payload = arguments.get_mutation_payload(params)
    if params['state'] == 'present':
        builds = [arguments.get_spec_payload(b, *b.keys()) for b in params['builds']]
        payload["builds"] = builds
    return payload


def main():
    required_if = [
        ("state", "present", ["builds"])
    ]
    module = AnsibleModule(
        required_if=required_if,
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec(
                "auth", "name", "namespace", "state", "labels", "annotations",
            ),
            builds=dict(
                type="list",
                elements="dict",
                options=dict(
                    url=dict(
                        required=True,
                    ),
                    sha512=dict(
                        required=True,
                    ),
                    filters=dict(
                        type="list",
                    ),
                    headers=dict(
                        type="dict",
                    ),
                )
            ),
        ),
    )

    msg = validate_module_params(module.params)
    if msg:
        module.fail_json(msg=msg)

    client = arguments.get_sensu_client(module.params["auth"])
    path = utils.build_core_v2_path(
        module.params["namespace"], "assets", module.params["name"],
    )
    payload = build_api_payload(module.params)

    try:
        changed, asset = utils.sync(
            module.params["state"], client, path, payload, module.check_mode, do_differ
        )
        module.exit_json(changed=changed, object=asset)
    except errors.Error as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
