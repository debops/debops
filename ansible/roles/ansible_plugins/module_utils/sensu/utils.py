# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.six.moves.urllib.parse import quote

from ansible.module_utils.sensu import errors


def do_differ(current, desired):
    if current is None:
        return True

    for key, value in desired.items():
        if value != current.get(key):
            return True

    return False


def sync(state, client, path, payload, check_mode, compare=do_differ):
    remote_object = get(client, path)

    if state == "absent" and remote_object is None:
        return False, None

    if state == "absent":
        if not check_mode:
            delete(client, path)
        return True, None

    # Making sure remote_object is present from here on

    if compare(remote_object, payload):
        if check_mode:
            return True, payload
        put(client, path, payload)
        return True, get(client, path)

    return False, remote_object


def _abort(msg, *args, **kwargs):
    raise errors.SyncError(msg.format(*args, **kwargs))


def get(client, path):
    resp = client.get(path)
    if resp.status not in (200, 404):
        _abort(
            "GET {0} failed with status {1}: {2}", path, resp.status, resp.data,
        )
    if resp.status == 200 and resp.json is None:
        _abort("Server returned invalid JSON {0}", resp.data)
    return resp.json


def delete(client, path):
    resp = client.delete(path)
    if resp.status != 204:
        _abort(
            "DELETE {0} failed with status {1}: {2}",
            path, resp.status, resp.data,
        )
    return None


def put(client, path, payload):
    resp = client.put(path, payload)
    if resp.status not in (200, 201):
        _abort(
            "PUT {0} failed with status {1}: {2}",
            path, resp.status, resp.data,
        )
    return None


def dict_to_single_item_dicts(data):
    return [{k: v} for k, v in data.items()]


def dict_to_key_value_strings(data):
    return ["{0}={1}".format(k, v) for k, v in data.items()]


def build_url_path(api_group, api_version, namespace, *parts):
    prefix = "/api/{0}/{1}/".format(api_group, api_version)
    if namespace:
        prefix += "namespaces/{0}/".format(quote(namespace, safe=""))
    return prefix + "/".join(quote(p, safe="") for p in parts if p)


def build_core_v2_path(namespace, *parts):
    return build_url_path("core", "v2", namespace, *parts)


def prepare_result_list(result):
    if isinstance(result, list):
        return result
    return [] if result is None else [result]
