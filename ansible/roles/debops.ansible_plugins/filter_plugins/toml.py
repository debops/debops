#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2019, Raphaël Droz <raphael.droz@gmail.com>
# GNU General Public License version 3 or any later version.

from __future__ import (absolute_import, division, print_function, unicode_literals)
__metaclass__ = type

import types
from ansible.module_utils import six

try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False

from ansible import errors

# See lib/ansible/plugins/inventory/toml.py
def convert_yaml_objects_to_native(obj):
    if isinstance(obj, dict):
        return dict((k, convert_yaml_objects_to_native(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return [convert_yaml_objects_to_native(v) for v in obj]
    elif isinstance(obj, six.text_type):
        return six.text_type(obj)
    else:
        return obj

def to_toml(dict_value):
    return toml.dumps(convert_yaml_objects_to_native(dict_value))

def from_toml(string):
    return toml.loads(string)

def replace_gitlab_token(dict_value, registered_runners_results):
    for runner in dict_value['runners']:
        for rr in registered_runners_results:
            if ('description' in rr and runner['name'] == rr['description']
                or 'name' in rr and runner['name'] == rr['name']):
                runner['token'] = rr['token']
                break
    return dict_value

def rejectattr_deep(dict_value, start = '_'):
    if isinstance(dict_value, dict):
        for k,v in dict_value.items():
            if k.startswith(start):
                dict_value.pop(k, None)
                # restart to avoid RuntimeError "dictionary changed size during iteration"
                return rejectattr_deep(dict_value, start)
            continue
        if isinstance(v, dict):
            dict_value[k] = rejectattr_deep(v, start)
        elif isinstance(v, list):
            dict_value[k] = [rejectattr_deep(element, start) if isinstance(element, dict)
                             else element
                             for element in v]
    return dict_value

class FilterModule(object):
    def filters(self):
        return {
            'to_toml': to_toml,
            'from_toml': from_toml,
            'replace_gitlab_token': replace_gitlab_token,
            'rejectattr_deep': rejectattr_deep
        }
