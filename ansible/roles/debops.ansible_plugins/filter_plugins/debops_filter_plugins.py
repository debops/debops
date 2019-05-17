# A set of custom Ansible filter plugins used by DebOps

# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2019 Robin Schneider <ypid@riseup.net>
# Copyright (C) 2017-2019 DebOps https://debops.org/


# This file is part of DebOps.
#
# DebOps is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DebOps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DebOps. If not, see <https://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
from past.builtins import basestring
from operator import itemgetter

try:
    unicode = unicode
except NameError:
    # py3
    unicode = str

__metaclass__ = type


def _check_if_key_in_nested_dict(key, dictionary):
    if isinstance(dictionary, dict):
        for k, v in dictionary.items():
            if k == key:
                return True
            elif isinstance(v, dict):
                if _check_if_key_in_nested_dict(key, v):
                    return True
            elif isinstance(v, list):
                for d in v:
                    if _check_if_key_in_nested_dict(key, d):
                        return True

    return False


def _parse_kv_value(current_data, new_data, data_index, *args, **kwargs):
    """Parse the parameter values and merge
    with existing ones conditionally.
    """

    if 'value' in new_data:
        old_value = current_data.get('value')
        old_state = current_data.get('state', 'present')
        new_value = new_data.get('value')

        if isinstance(new_value, (basestring, int, float, bool)):
            if (old_value is None or isinstance(old_value,
                                                (str, unicode, int,
                                                 float, bool, dict))):
                current_data.update({'value': new_value})

            if (old_value is not None and old_state in ['comment'] and
                    current_data['state'] != 'comment'):
                current_data.update({'state': 'present'})

        elif isinstance(new_value, list):
            if (old_value is None or isinstance(old_value, dict)):
                dict_value = current_data.get('value', {}).copy()

            elif isinstance(old_value, (str, unicode, int, float, bool)):
                dict_value = {}

            for element_index, element in enumerate(new_value):
                if isinstance(element, (str, unicode, int)):
                    dict_element = dict_value.get(element, {}).copy()
                    if not dict_element.get('name'):
                        dict_element.update({
                            'name': element,
                            'id': ((data_index * 10) + element_index),
                            'weight': dict_element.get('weight', 0),
                            'state': 'present'})

                        dict_element['real_weight'] = (
                            int(dict_element.get('id')) +
                            int(dict_element.get('weight')))

                        dict_value.update({element: dict_element})
                        current_data.update({'value': dict_value})

                elif (isinstance(element, dict) and
                        element.get('param', element.get('name')) and
                        element.get('state', 'present') != 'ignore'):
                    element_name = element.get('param', element.get('name'))

                    for cursor in ([element_name]
                                   if isinstance(element_name,
                                                 (str, unicode, int))
                                   else element_name):
                        dict_element = dict_value.get(cursor, {}).copy()
                        dict_element.update({
                            'name': cursor,
                            'id': ((data_index * 10) + element_index),
                            'weight': int(dict_element.get('weight', 0)),
                            'state': element.get('state', 'present')
                        })

                        if 'copy_id_from' in element:
                            if element.get('copy_id_from') in dict_value:
                                id_src = element.get('copy_id_from')
                                dict_element['id'] = (
                                    int(dict_value[id_src].get('id')) +
                                    int(dict_value[id_src].get('weight', 0)))

                        if 'weight' in element:
                            dict_element['weight'] = (
                                int(element.get('weight',
                                    dict_element.get('weight', 0))) +
                                int(dict_element.get('weight', 0)))

                        dict_element['real_weight'] = (
                            int(dict_element.get('id')) +
                            int(dict_element.get('weight')))

                        # Include any unknown keys
                        for key in element.keys():
                            if key not in ['name', 'state', 'id', 'weight',
                                           'real_weight', 'param',
                                           'copy_id_from']:
                                dict_element[key] = element.get(key)

                        dict_value.update({cursor: dict_element})
                        current_data.update({'value': dict_value})


def parse_kv_config(*args, **kwargs):
    """Return a parsed list of key/value configuration options"""

    input_args = []
    parsed_config = {}

    # Flatten the input list
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    for element_index, element in enumerate(input_args):
        if isinstance(element, dict):
            if (any(x in ['name'] for x in element) and
                    element.get('state', 'present') != 'ignore'):

                param_name = element.get('name')

                if element.get('state', 'present') == 'append':

                    # In append mode, don't create new config entries
                    if (parsed_config.get(param_name, {})
                            .get('state', 'present') == 'init'):
                        continue

                current_param = (parsed_config[param_name].copy()
                                 if param_name in parsed_config
                                 else {})

                if element.get('state', 'present') != 'append':
                    current_param['state'] = (element.get('state',
                                              current_param.get('state',
                                                                'present')))
                elif element.get('state', 'present') == 'append':
                    current_param['state'] = current_param.get('state',
                                                               'present')

                if (current_param['state'] == 'init' and
                        (_check_if_key_in_nested_dict('value', element) or
                        _check_if_key_in_nested_dict('value', current_param))):
                    current_param['state'] = 'present'

                current_param.update({
                    'name': param_name,  # in case of a new entry
                    'id': int(current_param.get('id', (element_index * 10))),
                    'weight': int(current_param.get('weight', 0)),
                    'separator': element.get('separator',
                                             current_param.get('separator',
                                                               False)),
                    'section': element.get('section',
                                           current_param.get('section',
                                                             'unknown'))
                })

                if 'copy_id_from' in element:
                    if element.get('copy_id_from') in parsed_config:
                        id_src = element.get('copy_id_from')
                        current_param['id'] = (
                            int(parsed_config[id_src].get('id')) +
                            int(parsed_config[id_src].get('weight', 0)))

                if 'weight' in element:
                    current_param['weight'] = (
                        int(element.get('weight',
                            current_param.get('weight', 0))) +
                        int(current_param.get('weight', 0)))

                current_param['real_weight'] = (
                    int(current_param.get('id')) +
                    int(current_param.get('weight')))

                _parse_kv_value(current_param, element,
                                current_param.get('id'))

                if 'option' in element:
                    current_param['option'] = element.get('option')

                if 'comment' in element:
                    current_param['comment'] = element.get('comment')

                merge_keys = ['options']
                if isinstance(kwargs.get('merge_keys'), list):
                    merge_keys.extend(kwargs.get('merge_keys'))

                for key_name in merge_keys:
                    if key_name in element:
                        current_options = current_param.get(key_name, [])
                        current_param[key_name] = parse_kv_config(
                            current_options + element.get(key_name),
                            merge_keys=merge_keys)

                # Include any unknown keys
                for unknown_key in element.keys():
                    if (unknown_key not in merge_keys
                            and unknown_key not in ['name', 'state', 'id', 'weight',
                                                    'real_weight', 'separator',
                                                    'value', 'comment', 'option',
                                                    'section']):
                        current_param[unknown_key] = element.get(unknown_key)

                parsed_config.update({param_name: current_param})

            # These parameters are special and should not be interpreted
            # directly as configuration options
            elif not all(x in ['name', 'option', 'state', 'comment',
                               'section', 'weight', 'value', 'copy_id_from']
                         for x in element):
                for key, value in element.items():
                    current_param = (parsed_config[key].copy()
                                     if key in parsed_config else {})
                    current_param.update({
                        'name': key,
                        'state': 'present',
                        'id': int(current_param.get('id',
                                                    (element_index * 10))),
                        'weight': int(current_param.get('weight', 0)),
                        'section': current_param.get('section', 'unknown')
                    })

                    current_param['real_weight'] = (
                        int(current_param.get('id')) +
                        int(current_param.get('weight')))

                    _parse_kv_value(current_param,
                                    {'value': value},
                                    current_param.get('id'))

                    parsed_config.update({key: current_param})

    # Expand the dictionary of configuration options into a list,
    # and return sorted by weight.
    output = []
    for key, params in parsed_config.items():
        if isinstance(params.get('value'), dict):
            params['value'] = sorted(
                params.get('value').values(),
                key=itemgetter('real_weight')
            )

        output.append(params)

    return sorted(output, key=itemgetter('real_weight'))


def parse_kv_items(*args, **kwargs):
    """Return a parsed list of with_items elements
    Optional arguments:

        empty
            dictionary, keys are parameter names which might be empty, values
            are key name or list of key names, first key with a value other
            than None will be used as the specified parameter. Examples:
                empty={'some_param':  'other_param',
                       'empty_param': ['param2', 'param1']}

        defaults
            dictionary, keys are parameter names, values are default values to
            use when a parameter is not specified. Examples:
                      defaults={'some_param': 'default_value'}

        merge_keys
            list of keys in the dictionary that will be merged together. If not
            specified, 'options' key instances will be merged by default.
    """

    input_args = []
    parsed_config = {}

    # Flatten the input list
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    for element_index, element in enumerate(input_args):

        element_state = element.get('state', 'present')

        if isinstance(element, dict):
            if (any(x in ['name'] for x in element) and
                    element_state != 'ignore'):

                param_name = element.get('name')

                if element_state == 'append':

                    # In append mode, don't create new config entries
                    if (param_name not in parsed_config or
                        parsed_config[param_name].get('state',
                                                      'present') == 'init'):
                        continue

                current_param = (parsed_config[param_name].copy()
                                 if param_name in parsed_config
                                 else {})

                if element_state != 'append':
                    current_param['state'] = (element.get('state',
                                              current_param.get('state',
                                                                'present')))
                elif element_state == 'append':
                    current_param['state'] = current_param.get('state',
                                                               'present')

                if (current_param['state'] == 'init' and
                        (_check_if_key_in_nested_dict('value', element) or
                        _check_if_key_in_nested_dict('value', current_param))):
                    current_param['state'] = 'present'

                current_param.update({
                    'name': param_name,  # in case of a new entry
                    'id': int(current_param.get('id', (element_index * 10))),
                    'weight': int(current_param.get('weight', 0)),
                    'separator': element.get('separator',
                                             current_param.get('separator',
                                                               False))
                })

                if 'copy_id_from' in element:
                    if element.get('copy_id_from') in parsed_config:
                        id_src = element.get('copy_id_from')
                        current_param['id'] = (
                            int(parsed_config[id_src].get('id')) +
                            int(parsed_config[id_src].get('weight', 0)))

                if 'weight' in element:
                    current_param['weight'] = (
                        int(element.get('weight',
                            current_param.get('weight', 0))) +
                        int(current_param.get('weight', 0)))

                current_param['real_weight'] = (
                    int(current_param.get('id')) +
                    int(current_param.get('weight')))

                if 'comment' in element:
                    current_param['comment'] = element.get('comment')

                # Set any default keys defined for the filter
                if (kwargs.get('defaults') and
                        isinstance(kwargs.get('defaults'), dict)):
                    defargs = kwargs.get('defaults')

                    for key in defargs.keys():
                        current_param[key] = (
                            current_param.get(key,
                                              defargs.get(key)))

                merge_keys = ['options']
                if isinstance(kwargs.get('merge_keys'), list):
                    merge_keys.extend(kwargs.get('merge_keys'))

                for key_name in merge_keys:
                    if key_name in element:
                        current_options = current_param.get(key_name, [])
                        current_param[key_name] = parse_kv_config(
                            current_options + element.get(key_name),
                            merge_keys=kwargs.get('merge_keys'))


                known_keys = ['name', 'state', 'id', 'weight',
                              'real_weight', 'separator',
                              'comment', 'options']
                if isinstance(kwargs.get('merge_keys'), list):
                    known_keys.extend(kwargs.get('merge_keys'))

                # Include any unknown keys
                for unknown_key in element.keys():
                    if unknown_key not in known_keys:
                        current_param[unknown_key] = element.get(unknown_key)

                # Fill any empty keys using other keys
                if isinstance(kwargs.get('empty'), dict):
                    emptargs = kwargs.get('empty')

                    for key in emptargs.keys():
                        if key not in current_param:
                            for thing in list(emptargs[key]):
                                current_param[key] = current_param.get(thing)
                                if key in current_param:
                                    break

                parsed_config.update({param_name: current_param})

    # Expand the dictionary of configuration options into a list,
    # and return sorted by weight
    output = []
    for key, params in parsed_config.items():
        if isinstance(params.get('value'), dict):
            params['value'] = sorted(
                params.get('value').values(),
                key=itemgetter('real_weight')
            )

        output.append(params)

    return sorted(output, key=itemgetter('real_weight'))


class FilterModule(object):
    """Register custom filter plugins in Ansible"""

    def filters(self):
        return {
            'parse_kv_config': parse_kv_config,
            'parse_kv_items': parse_kv_items
        }


if __name__ == '__main__':
    import unittest
    from nose.tools import assert_equal
    import textwrap
    import yaml

    class Test(unittest.TestCase):

        def test_parse_kv_config(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: 'test'
            - name: 'local2'
              value: 'test2'
            - name: 'local'
              value: 'test3'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - id: 0
              name: local
              real_weight: 0
              section: unknown
              separator: false
              state: present
              value: test3
              weight: 0
            - id: 10
              name: local2
              real_weight: 10
              section: unknown
              separator: false
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            #  print(yaml.dump(items, default_flow_style=False))
            #  print(yaml.dump(expected_items, default_flow_style=False))

            assert_equal(items, expected_items)

        def test_parse_kv_items_empty(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'name should be used as comment'
              options:

                - name: 'second level is ignored'
                  service: 'second level is ignored so service will not become the comment'
                  value: 'test'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - comment: name should be used as comment
              id: 0
              name: name should be used as comment
              options:
              - id: 0
                name: second level is ignored
                real_weight: 0
                section: unknown
                separator: false
                service: second level is ignored so service will not become the comment
                state: present
                value: test
                weight: 0
              real_weight: 0
              separator: false
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items, empty={'comment': ['service', 'name']})

            #  print(yaml.dump(items, default_flow_style=False))
            #  print(yaml.dump(expected_items, default_flow_style=False))

            assert_equal(items, expected_items)

        def test_parse_kv_items_defaults(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'something'
              key1: 'existing'
              value: 'something'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - id: 0
              key1: existing
              key2: value2
              name: something
              real_weight: 0
              separator: false
              state: present
              value: something
              weight: 0
            '''))

            items = parse_kv_items(input_items, defaults={'key1': 'value1', 'key2': 'value2'})

            #  print(yaml.dump(items, default_flow_style=False))
            #  print(yaml.dump(expected_items, default_flow_style=False))

            assert_equal(items, expected_items)

        def test_parse_kv_items_merge_keys(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'something'
              key1: 'existing'
              options:

                - name: 'nested1'
                  value: 'value1'

            - name: 'something'
              options:

                - name: 'nested2'
                  value: 'value2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - id: 0
              key1: existing
              name: something
              options:
              - id: 0
                name: nested1
                real_weight: 0
                section: unknown
                separator: false
                state: present
                value: value1
                weight: 0
              - id: 10
                name: nested2
                real_weight: 10
                section: unknown
                separator: false
                state: present
                value: value2
                weight: 0
              real_weight: 0
              separator: false
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items, merge_keys=['test'])

            #  print(yaml.dump(items, default_flow_style=False))
            #  print(yaml.dump(expected_items, default_flow_style=False))

            assert_equal(items, expected_items)

        def test_parse_kv_items(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'should-stay-init'
              options:

                - name: 'local'
                  value: 'test'

              state: 'init'


            - name: 'should-become-present'
              options:

                - name: 'local'
                  value: 'test'

              state: 'init'

            - name: 'should-become-present'
              options:

                - name: 'local'
                  value: 'test2'


            - name: 'should-become-present2'
              options:

                - name: 'local'
                  value: 'test'
                  state: 'init'

              state: 'init'

            - name: 'should-become-present2'
              options:

                - name: 'local'
                  value: 'test2'


            - name: 'should-become-present3'
              options:

                - name: 'local1'
                  comment: 'This comment should survive.'
                  options:

                    - name: 'local2'
                      value: 'test'
                      state: 'init'

                  state: 'init'

                - name: 'external1'
                  options:

                    - name: 'external2'
                      value: 'test'
                      state: 'init'

                  state: 'init'


            - name: 'should-become-present3'
              options:

                - name: 'local1'
                  options:

                    - name: 'local2'
                      value: 'test2'

                - name: 'external1'
                  options:

                    - name: 'external2'
                      value: 'test'

            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - id: 0
              name: should-stay-init
              options:
              - id: 0
                name: local
                real_weight: 0
                section: unknown
                separator: false
                state: present
                value: test
                weight: 0
              real_weight: 0
              separator: false
              state: init
              weight: 0
            - id: 10
              name: should-become-present
              options:
              - id: 0
                name: local
                real_weight: 0
                section: unknown
                separator: false
                state: present
                value: test2
                weight: 0
              real_weight: 10
              separator: false
              state: present
              weight: 0
            - id: 30
              name: should-become-present2
              options:
              - id: 0
                name: local
                real_weight: 0
                section: unknown
                separator: false
                state: present
                value: test2
                weight: 0
              real_weight: 30
              separator: false
              state: present
              weight: 0
            - id: 50
              name: should-become-present3
              options:
              - comment: This comment should survive.
                id: 0
                name: local1
                options:
                - id: 0
                  name: local2
                  real_weight: 0
                  section: unknown
                  separator: false
                  state: present
                  value: test2
                  weight: 0
                real_weight: 0
                section: unknown
                separator: false
                state: present
                weight: 0
              - id: 10
                name: external1
                options:
                - id: 0
                  name: external2
                  real_weight: 0
                  section: unknown
                  separator: false
                  state: present
                  value: test
                  weight: 0
                real_weight: 10
                section: unknown
                separator: false
                state: present
                weight: 0
              real_weight: 50
              separator: false
              state: present
              weight: 0
            '''))

            #  print("----------------------------")
            #  print(yaml.dump(parse_kv_items(input_items), default_flow_style=False))

            assert_equal(parse_kv_items(input_items), expected_items)

    unittest.main()
