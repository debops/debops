# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import env_fallback

from ansible.module_utils.sensu import client


SHARED_SPECS = dict(
    auth=dict(
        type="dict",
        apply_defaults=True,
        options=dict(
            user=dict(
                default="admin",
                fallback=(env_fallback, ["SENSU_USER"]),
            ),
            password=dict(
                default="P@ssw0rd!",
                no_log=True,
                fallback=(env_fallback, ["SENSU_PASSWORD"]),
            ),
            url=dict(
                default="http://localhost:8080",
                fallback=(env_fallback, ["SENSU_URL"]),
            ),
            api_key=dict(
                fallback=(env_fallback, ["SENSU_API_KEY"]),
            ),
        ),
    ),
    state=dict(
        default="present",
        choices=["present", "absent"],
    ),
    name=dict(
        required=True,
    ),
    namespace=dict(
        default="default",
        fallback=(env_fallback, ["SENSU_NAMESPACE"]),
    ),
    labels=dict(
        type="dict",
        default={},
    ),
    annotations=dict(
        type="dict",
        default={},
    ),
)


def get_spec(*param_names):
    return {p: SHARED_SPECS[p] for p in param_names}


def get_spec_payload(source, *wanted_params):
    return {
        k: source[k] for k in wanted_params if source.get(k) is not None
    }


def get_mutation_payload(source, *wanted_params):
    payload = get_spec_payload(source, *wanted_params)
    payload["metadata"] = dict(
        name=source["name"],
    )
    # Cluster-wide objects are not limited to a single namespace. This is why we set
    # metadata.namespace field only if namespace is present in parameters.
    if "namespace" in source:
        if not source["namespace"]:
            # We are raising an exception here for the sake of sanity test.
            raise AssertionError("BUG: namespace should not be None")
        payload["metadata"]["namespace"] = source["namespace"]

    for kind in "labels", "annotations":
        if source.get(kind):
            payload["metadata"][kind] = {
                k: str(v) for k, v in source[kind].items()
            }
    return payload


def get_sensu_client(auth):
    return client.Client(
        auth["url"], auth["user"], auth["password"], auth["api_key"],
    )
