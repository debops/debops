# A set of custom Ansible filter plugins used by DebOps

# Copyright (C) 2017-2019 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2019      Robin Schneider <ypid@riseup.net>
# Copyright (C) 2017-2019 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later


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

__metaclass__ = type

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


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


def _handle_weight(element, current_param):
    if 'weight' in element:
        current_param['weight'] = int(element['weight'])


def _detect_anchor_cycles(graph):
    """Raise ValueError if the anchor_to graph contains a cycle.

    ``graph`` maps an item name to the name it is anchored to. A cycle means
    the items can never be ordered relative to each other, so it is treated as
    a fatal configuration error.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node, path):
        color[node] = GRAY
        neighbor = graph.get(node)
        if neighbor and neighbor in color:
            if color[neighbor] == GRAY:
                path.append(neighbor)
                raise ValueError(
                    "Circular anchor_to dependency detected: "
                    + " -> ".join(str(n) for n in path))
            elif color[neighbor] == WHITE:
                path.append(neighbor)
                dfs(neighbor, path)
                path.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node, [node])


def _sort_parsed_items(items, name_key='name'):
    """Sort items by weight zone, first_index, and anchor_to relationships.

    Sorting rules:
      - Items without anchor_to: sort by zone (neg→top, zero→middle, pos→bottom)
        then by first_index (original position of first occurrence).
      - Items with anchor_to: positioned relative to anchor item; weight sign
        determines direction (neg→before, zero/pos→after). Cross-zone anchor_to
        overrides the item's zone.
      - Multiple items anchored to the same target: sorted by first_index
        and inserted as a contiguous block.
      - Anchor chains (A→B→C): resolved via topological sort.
      - Circular anchor_to chains: raise ValueError.
    """

    def _zone(item):
        w = item.get('weight', 0)
        try:
            w = int(w)
        except (ValueError, TypeError):
            w = 0
        return 0 if w < 0 else (1 if w == 0 else 2)

    name_map = {item[name_key]: item for item in items}

    anchored = []
    unanchored = []
    for item in items:
        at = item.get('anchor_to')
        if at and at in name_map:
            anchored.append(item)
        else:
            unanchored.append(item)

    unanchored.sort(key=lambda x: (_zone(x), x.get('first_index', 0)))

    graph = {item[name_key]: item['anchor_to'] for item in anchored}
    _detect_anchor_cycles(graph)

    target_groups = {}
    for item in anchored:
        target = item['anchor_to']
        if target not in target_groups:
            target_groups[target] = []
        target_groups[target].append(item)

    for group in target_groups.values():
        group.sort(key=lambda x: x.get('first_index', 0))

    target_dep = {}
    for target, group in target_groups.items():
        for item in group:
            if item[name_key] in target_groups:
                if target not in target_dep:
                    target_dep[target] = []
                target_dep[target].append(item[name_key])

    all_targets = list(target_groups.keys())
    in_degree = {t: 0 for t in all_targets}
    for deps in target_dep.values():
        for dep in deps:
            in_degree[dep] = in_degree.get(dep, 0) + 1

    queue = [t for t in all_targets if in_degree.get(t, 0) == 0]
    target_order = []
    while queue:
        t = queue.pop(0)
        target_order.append(t)
        for dep in target_dep.get(t, []):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    result = list(unanchored)

    for target in target_order:
        if target not in target_groups:
            continue
        group = target_groups[target]

        target_pos = None
        for i, item in enumerate(result):
            if item[name_key] == target:
                target_pos = i
                break

        if target_pos is None:
            result.extend(group)
        else:
            before = [item for item in group if item.get('weight', 0) < 0]
            after = [item for item in group if item.get('weight', 0) >= 0]

            for item in reversed(before):
                result.insert(target_pos, item)

            target_pos = None
            for i, item in enumerate(result):
                if item[name_key] == target:
                    target_pos = i
                    break

            for i, item in enumerate(after):
                result.insert(target_pos + 1 + i, item)

    return result


def _parse_kv_value(current_data, new_data, data_index):
    """Parse the parameter values and merge
    with existing ones conditionally.
    """

    if 'value' in new_data:
        old_value = current_data.get('value')
        new_value = new_data['value']
        new_value_cast = new_data.get('value_cast', None)

        if (new_value is None or
                isinstance(new_value, (basestring, int, float, bool))):
            if (old_value is None or isinstance(old_value,
                                                (basestring, int,
                                                 float, bool, dict))):
                if new_value_cast in ['null', 'none', 'None']:
                    current_data['value'] = None
                elif new_value_cast in ['int', 'integer']:
                    current_data['value'] = int(new_value)
                elif new_value_cast in ['str', 'string']:
                    current_data['value'] = str(new_value)
                elif new_value_cast in ['bool', 'boolean']:
                    current_data['value'] = bool(new_value)
                elif new_value_cast == 'float':
                    current_data['value'] = float(new_value)
                else:
                    current_data['value'] = new_value

        elif isinstance(new_value, list):
            if isinstance(old_value, dict):
                dict_value = current_data.get('value', {}).copy()
            else:
                dict_value = {}

            for element_index, element in enumerate(new_value):
                if isinstance(element, (basestring, int)):
                    dict_element = dict_value.get(element, {}).copy()
                    if not dict_element.get('name'):
                        dict_element.update({
                            'name': element,
                            'first_index': element_index,
                            'weight': int(dict_element.get('weight', 0)),
                            'state': 'present'})

                        dict_value[element] = dict_element
                        current_data['value'] = dict_value

                elif (isinstance(element, dict) and
                        element.get('param', element.get('name')) and
                        element.get('state', 'present') != 'ignore'):
                    element_name = element.get('param', element.get('name'))

                    for cursor in ([element_name]
                                   if isinstance(element_name,
                                                 (basestring, int))
                                   else element_name):
                        dict_element = dict_value.get(cursor, {}).copy()
                        if 'first_index' not in dict_element:
                            dict_element['first_index'] = element_index
                        dict_element.update({
                            'name': cursor,
                            'weight': int(element.get('weight',
                                                      dict_element.get(
                                                          'weight', 0))),
                            'state': element.get('state', 'present')
                        })

                        if 'anchor_to' in element:
                            dict_element['anchor_to'] = element['anchor_to']

                        if 'weight' in element:
                            dict_element['weight'] = int(element['weight'])

                        if 'option' in element or 'alias' in element:
                            alias_value = element.get('alias',
                                                      element.get(
                                                          'option'))
                            dict_element['option'] = alias_value
                            dict_element['alias'] = alias_value

                        for key in element.keys():
                            if key not in ['name', 'state', 'id', 'weight',
                                           'param', 'option', 'alias',
                                           'first_index']:
                                dict_element[key] = element.get(key)

                        dict_value.update({cursor: dict_element})
                        current_data.update({'value': dict_value})


def parse_kv_config(*args, **kwargs):
    """Return a parsed list of key/value configuration options

    Optional arguments:

        name
            string, name of the primary dictionary key used as an indicator to
            merge the related dictionaries together. If not specified, 'name'
            will be set as default.
    """
    name = kwargs.get('name', "name")
    input_args = []
    parsed_config = {}

    # Flatten the input list.
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    for element_index, element in enumerate(input_args):

        if isinstance(element, (basestring)):

            # This is a simple string, let's make it a dictionary so that it
            # can be correctly processed.
            # We assume that the string should be a 'name' parameter.
            element = {name: element}

        if isinstance(element, dict):
            if any(x in [name] for x in element):

                if element.get('state', 'present') != 'ignore':

                    param_name = element.get(name)

                    if element.get('state', 'present') == 'append':

                        # In append mode, don't create new config entries
                        if (parsed_config.get(param_name, {})
                                .get('state', 'present') == 'init'):
                            continue

                    current_param = (parsed_config[param_name].copy()
                                     if param_name in parsed_config
                                     else {})

                    if 'first_index' not in current_param:
                        current_param['first_index'] = element_index

                    if element.get('state', 'present') == 'append':
                        current_param['state'] = current_param.get(
                                'state', 'present')
                    else:
                        current_param['state'] = (
                            element.get('state', current_param.get(
                                'state', 'present')))

                    if (current_param['state'] == 'init' and
                        (element.get('state', 'present') != 'init' and
                            _check_if_key_in_nested_dict(
                            'value', current_param))):
                        current_param['state'] = 'present'

                    current_param.update({
                        name: param_name,  # in case of a new entry
                        'weight': int(element.get('weight',
                                                  current_param.get(
                                                      'weight', 0)))
                    })

                    _handle_weight(element, current_param)

                    if 'anchor_to' in element:
                        current_param['anchor_to'] = element['anchor_to']

                    _parse_kv_value(current_param, element,
                                    current_param.get('first_index',
                                                      element_index))

                    if 'option' in element or 'alias' in element:
                        alias_value = element.get('alias',
                                                  element.get('option'))
                        current_param['option'] = alias_value
                        current_param['alias'] = alias_value

                    if 'comment' in element:
                        current_param['comment'] = element.get('comment')

                    merge_keys = []
                    if isinstance(kwargs.get('merge_keys'), list):
                        merge_keys.extend(kwargs.get('merge_keys'))

                    if 'options' not in merge_keys:
                        merge_keys.append('options')

                    for key_name in merge_keys:
                        if key_name in element:
                            current_options = current_param.get(key_name, [])
                            current_param[key_name] = parse_kv_config(
                                current_options + element.get(key_name),
                                merge_keys=merge_keys)

                    # Include any unknown keys
                    for unknown_key in element.keys():
                        if (unknown_key not in merge_keys
                            and unknown_key not in [name, 'state', 'id',
                                                    'weight',
                                                    'value',
                                                    'comment', 'option',
                                                    'alias', 'first_index',
                                                    'anchor_to']):
                            current_param[unknown_key] = (
                                    element.get(unknown_key))

                    parsed_config.update({param_name: current_param})

            # These parameters are special and should not be interpreted
            # directly as configuration options
            elif not all(x in [name, 'option', 'alias', 'state', 'comment',
                               'weight', 'value', 'anchor_to']
                         for x in element):
                for key, value in element.items():
                    current_param = (parsed_config[key].copy()
                                     if key in parsed_config else {})
                    if 'first_index' not in current_param:
                        current_param['first_index'] = element_index
                    current_param.update({
                        name: key,
                        'state': 'present',
                        'weight': int(current_param.get('weight', 0))
                    })

                    _parse_kv_value(current_param,
                                    {'value': value},
                                    current_param.get('first_index',
                                                      element_index))

                    parsed_config.update({key: current_param})

    items = list(parsed_config.values())
    sorted_items = _sort_parsed_items(items, name_key=name)

    for item in sorted_items:
        if isinstance(item.get('value'), dict):
            value_items = list(item['value'].values())
            item['value'] = _sort_parsed_items(value_items)

    for idx, item in enumerate(sorted_items):
        item['id'] = idx
        if isinstance(item.get('value'), list):
            for vidx, vitem in enumerate(item['value']):
                if isinstance(vitem, dict):
                    vitem['id'] = vidx

    return sorted_items


def parse_kv_items(*args, **kwargs):
    """Return a parsed list of with_items elements
    Optional arguments:

        name
            string, name of the primary dictionary key used as an indicator to
            merge the related dictionaries together. If not specified, 'name'
            will be set as default.

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
    name = kwargs.get('name', "name")
    empty = kwargs.get('empty', {})
    defaults = kwargs.get('defaults', {})
    merge_keys = list(set(kwargs.get('merge_keys', set())))

    if 'options' not in merge_keys:
        merge_keys.append('options')

    input_args = []

    # Flatten the input list.
    for sublist in args:
        input_args.extend(sublist)

    parsed_config = {}

    for element_index, element in enumerate(input_args):

        if isinstance(element, dict):
            element_state = element.get('state', 'present')
        elif isinstance(element, (basestring)):

            # This is a simple string, let's make it a dictionary so that it
            # can be correctly processed.
            # We assume that the string should be a 'name' parameter.
            element = {name: element}
            element_state = 'present'

        if isinstance(element, dict):
            if (any(x in [name] for x in element) and
                    element_state != 'ignore'):

                param_name = element.get(name)

                if element_state == 'append':

                    # In append mode, don't create new config entries.
                    if (param_name not in parsed_config or
                        parsed_config[param_name].get('state',
                                                      'present') == 'init'):
                        continue

                current_param = (parsed_config[param_name].copy()
                                 if param_name in parsed_config
                                 else {})

                if 'first_index' not in current_param:
                    current_param['first_index'] = element_index

                if element_state == 'append':
                    current_param['state'] = current_param.get(
                            'state', 'present')
                else:
                    current_param['state'] = (
                        element.get('state', current_param.get(
                            'state', 'present')))

                if (current_param['state'] == 'init' and
                        (element_state != 'init' and
                            _check_if_key_in_nested_dict(
                                'value', current_param))):
                    current_param['state'] = 'present'

                current_param.update({
                    name: param_name,
                    'weight': int(element.get('weight',
                                              current_param.get(
                                                  'weight', 0)))
                })

                _handle_weight(element, current_param)

                if 'anchor_to' in element:
                    current_param['anchor_to'] = element['anchor_to']

                if 'option' in element or 'alias' in element:
                    alias_value = element.get('alias',
                                              element.get('option'))
                    current_param['option'] = alias_value
                    current_param['alias'] = alias_value

                if 'comment' in element:
                    current_param['comment'] = element.get('comment')

                # Set any default keys defined for the filter.
                for k, v in defaults.items():
                    current_param[k] = current_param.get(k, v)

                for key_name in merge_keys:
                    if key_name in element:
                        current_options = current_param.get(key_name, [])
                        current_param[key_name] = parse_kv_config(
                            current_options + element.get(key_name),
                            merge_keys=merge_keys)

                known_keys = [name, 'state', 'id', 'weight',
                              'comment', 'options', 'first_index',
                              'anchor_to', 'option', 'alias']

                # Include any unknown keys.
                for unknown_key in element.keys():
                    if (unknown_key not in known_keys and
                            unknown_key not in merge_keys):
                        current_param[unknown_key] = element.get(unknown_key)

                # Fill any empty keys using other keys.
                for key_to_set, keys_to_check in empty.items():
                    if key_to_set in current_param:
                        continue

                    for key_to_check in keys_to_check:
                        if key_to_check in current_param:
                            current_param[key_to_set] = \
                                    current_param[key_to_check]
                            break

                parsed_config[param_name] = current_param

    items = list(parsed_config.values())
    sorted_items = _sort_parsed_items(items, name_key=name)

    for item in sorted_items:
        if isinstance(item.get('value'), dict):
            value_items = list(item['value'].values())
            item['value'] = _sort_parsed_items(value_items)

    for idx, item in enumerate(sorted_items):
        item['id'] = idx
        if isinstance(item.get('value'), list):
            for vidx, vitem in enumerate(item['value']):
                if isinstance(vitem, dict):
                    vitem['id'] = vidx

    return sorted_items


class FilterModule(object):
    """Register custom filter plugins in Ansible"""

    def filters(self):
        return {
            'parse_kv_config': parse_kv_config,
            'parse_kv_items': parse_kv_items
        }


if __name__ == '__main__':
    import unittest
    import textwrap
    import yaml

    class Test(unittest.TestCase):

        def test_parse_kv_value_simple(self):
            current_data = yaml.safe_load(textwrap.dedent('''
            name: 'local'
            value: 'test'
            '''))

            new_data = yaml.safe_load(textwrap.dedent('''
            name: 'local'
            value: 'test2'
            '''))

            _parse_kv_value(current_data, new_data, 0)

            self.assertEqual(current_data, new_data)

        def test_parse_kv_value_mixed(self):
            current_data = yaml.safe_load(textwrap.dedent('''
            name: 'local'
            value:
              - 'alpha'
              - 'test'
            '''))

            new_data = yaml.safe_load(textwrap.dedent('''
            name: 'local'
            value:
              - 'beta'
            '''))

            expected_data = yaml.safe_load(textwrap.dedent('''
            name: local
            value:
              beta:
                first_index: 0
                name: beta
                state: present
                weight: 0
            '''))

            _parse_kv_value(current_data, new_data, 0)

            self.assertEqual(current_data, expected_data)

        def test_parse_kv_config(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: 'test'
            - name: 'local2'
              value: 'test2'
            - name: 'local'
              value: 'test3'
            - name: 'local_null'
              value: null
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value: test3
              weight: 0
            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            - first_index: 3
              id: 2
              name: local_null
              state: present
              value: null
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_absent(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: 'test'
            - name: 'local2'
              value: 'test2'
            - name: 'local'
              value: 'test3'
            - name: 'local_null'
              value: null
              state: 'absent'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value: test3
              weight: 0
            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            - first_index: 3
              id: 2
              name: local_null
              state: absent
              value: null
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_init(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: 'test'
            - name: 'local2'
              value: 'test2'
            - name: 'local'
              value: 'test3'
            - name: 'local_null'
              value: null
              state: 'init'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value: test3
              weight: 0
            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            - first_index: 3
              id: 2
              name: local_null
              state: init
              value: null
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_ignore(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: 'test'
            - name: 'local2'
              value: 'test2'
            - name: 'local'
              value: 'test3'
            - name: 'local_null'
              value: null
              state: 'ignore'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value: test3
              weight: 0
            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_ignore_existing(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: 'test'
            - name: 'local2'
              value: 'test2'
            - name: 'local'
              value: 'test3'
              state: 'ignore'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value: test
              weight: 0
            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_simple_string(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - 'simple_string'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: simple_string
              state: present
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_null_to_list(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value: null
            - name: 'local'
              value: ['test1']
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value:
              - first_index: 0
                id: 0
                name: test1
                state: present
                weight: 0
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_renamed(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - renamed: 'local'
              value: 'test'
            - renamed: 'local2'
              value: 'test2'
            - renamed: 'local'
              value: 'test3'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              renamed: local
              state: present
              value: test3
              weight: 0
            - first_index: 1
              id: 1
              renamed: local2
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_config(input_items, name='renamed')

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_simple_string(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - 'simple_string'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: simple_string
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_empty(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'name should be used as comment'
              options:

                - name: 'second level is ignored'
                  service: |-
                    second level is ignored so service will not become the
                    comment
                  value: 'test'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - comment: name should be used as comment
              first_index: 0
              id: 0
              name: name should be used as comment
              options:
              - first_index: 0
                id: 0
                name: second level is ignored
                service: |-
                    second level is ignored so service will not become the
                    comment
                state: present
                value: test
                weight: 0
              state: present
              weight: 0
            '''))

            items = parse_kv_items(
                    input_items, empty={'comment': ['service', 'name']})

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_defaults(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'something'
              key1: 'existing'
              value: 'something'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              key1: existing
              key2: value2
              name: something
              state: present
              value: something
              weight: 0
            '''))

            items = parse_kv_items(
                    input_items, defaults={'key1': 'value1', 'key2': 'value2'})

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_value_string_list(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'protocols'
              value:
                - '!SSLv2'
                - '!SSLv3'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: protocols
              state: present
              value:
                - '!SSLv2'
                - '!SSLv3'
              weight: 0
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_merge_keys(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'something'
              key1: 'existing'
              options:

                - name: 'nested1'
                  value: 'value1'

              test:

                - name: 'test_nested1'
                  value: 'test_value1'

            - name: 'something'
              options:

                - name: 'nested2'
                  value: 'value2'

              test:

                - name: 'test_nested2'
                  value: 'test_value2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              key1: existing
              name: something
              options:
              - first_index: 0
                id: 0
                name: nested1
                state: present
                value: value1
                weight: 0
              - first_index: 1
                id: 1
                name: nested2
                state: present
                value: value2
                weight: 0
              test:
              - first_index: 0
                id: 0
                name: test_nested1
                state: present
                value: test_value1
                weight: 0
              - first_index: 1
                id: 1
                name: test_nested2
                state: present
                value: test_value2
                weight: 0
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items, merge_keys=['test'])

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_anchor_to(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'second'
              weight: 1
              value: 'value1'

            - name: 'first'
              anchor_to: 'second'
              weight: -1
              value: 'value2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - anchor_to: second
              first_index: 1
              id: 0
              name: first
              state: present
              value: value2
              weight: -1
            - first_index: 0
              id: 1
              name: second
              state: present
              value: value1
              weight: 1
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_anchor_to_chain(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'C'
              value: 'c_value'

            - name: 'B'
              anchor_to: 'C'
              weight: 1
              value: 'b_value'

            - name: 'A'
              anchor_to: 'B'
              weight: 1
              value: 'a_value'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: C
              state: present
              value: c_value
              weight: 0
            - anchor_to: C
              first_index: 1
              id: 1
              name: B
              state: present
              value: b_value
              weight: 1
            - anchor_to: B
              first_index: 2
              id: 2
              name: A
              state: present
              value: a_value
              weight: 1
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_anchor_to_same_target(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'target'
              value: 'main'

            - name: 'second'
              anchor_to: 'target'
              weight: 1
              value: 'second_value'

            - name: 'first'
              anchor_to: 'target'
              weight: 1
              value: 'first_value'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: target
              state: present
              value: main
              weight: 0
            - anchor_to: target
              first_index: 1
              id: 1
              name: second
              state: present
              value: second_value
              weight: 1
            - anchor_to: target
              first_index: 2
              id: 2
              name: first
              state: present
              value: first_value
              weight: 1
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_anchor_to_cross_zone(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'middle_item'
              weight: 0
              value: 'middle'

            - name: 'anchored_after'
              anchor_to: 'middle_item'
              weight: 5
              value: 'after_middle'

            - name: 'anchored_before'
              anchor_to: 'middle_item'
              weight: -3
              value: 'before_middle'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - anchor_to: middle_item
              first_index: 2
              id: 0
              name: anchored_before
              state: present
              value: before_middle
              weight: -3
            - first_index: 0
              id: 1
              name: middle_item
              state: present
              value: middle
              weight: 0
            - anchor_to: middle_item
              first_index: 1
              id: 2
              name: anchored_after
              state: present
              value: after_middle
              weight: 5
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_anchor_to_cycle(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'A'
              anchor_to: 'B'
              value: 'a'

            - name: 'B'
              anchor_to: 'A'
              value: 'b'
            '''))

            with self.assertRaises(ValueError):
                parse_kv_items(input_items)

        def test_parse_kv_items_weight_override(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'item'
              weight: 5
              value: 'first'

            - name: 'item'
              weight: 10
              value: 'second'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: item
              state: present
              value: second
              weight: 10
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_weight_zones(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'bottom1'
              weight: 5
              value: 'bottom1'

            - name: 'top1'
              weight: -5
              value: 'top1'

            - name: 'middle1'
              weight: 0
              value: 'middle1'

            - name: 'bottom2'
              weight: 3
              value: 'bottom2'

            - name: 'top2'
              weight: -10
              value: 'top2'

            - name: 'middle2'
              weight: 0
              value: 'middle2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 1
              id: 0
              name: top1
              state: present
              value: top1
              weight: -5
            - first_index: 4
              id: 1
              name: top2
              state: present
              value: top2
              weight: -10
            - first_index: 2
              id: 2
              name: middle1
              state: present
              value: middle1
              weight: 0
            - first_index: 5
              id: 3
              name: middle2
              state: present
              value: middle2
              weight: 0
            - first_index: 0
              id: 4
              name: bottom1
              state: present
              value: bottom1
              weight: 5
            - first_index: 3
              id: 5
              name: bottom2
              state: present
              value: bottom2
              weight: 3
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items(self):
            input_items1 = yaml.safe_load(textwrap.dedent('''
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
            '''))

            input_items2 = yaml.safe_load(textwrap.dedent('''
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
            - first_index: 0
              id: 0
              name: should-stay-init
              options:
              - first_index: 0
                id: 0
                name: local
                state: present
                value: test
                weight: 0
              state: init
              weight: 0
            - first_index: 1
              id: 1
              name: should-become-present
              options:
              - first_index: 0
                id: 0
                name: local
                state: present
                value: test2
                weight: 0
              state: present
              weight: 0
            - first_index: 3
              id: 2
              name: should-become-present2
              options:
              - first_index: 0
                id: 0
                name: local
                state: present
                value: test2
                weight: 0
              state: present
              weight: 0
            - first_index: 5
              id: 3
              name: should-become-present3
              options:
              - comment: This comment should survive.
                first_index: 0
                id: 0
                name: local1
                options:
                - first_index: 0
                  id: 0
                  name: local2
                  state: present
                  value: test2
                  weight: 0
                state: present
                weight: 0
              - first_index: 1
                id: 1
                name: external1
                options:
                - first_index: 0
                  id: 0
                  name: external2
                  state: present
                  value: test
                  weight: 0
                state: present
                weight: 0
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items1, input_items2)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_renamed(self):
            input_items1 = yaml.safe_load(textwrap.dedent('''
            - renamed: 'should-stay-init'
              options:

                - name: 'local'
                  value: 'test'

              state: 'init'


            - renamed: 'should-become-present'
              options:

                - name: 'local'
                  value: 'test'

              state: 'init'

            - renamed: 'should-become-present'
              options:

                - name: 'local'
                  value: 'test2'


            - renamed: 'should-become-present2'
              options:

                - name: 'local'
                  value: 'test'
                  state: 'init'

              state: 'init'

            - renamed: 'should-become-present2'
              options:

                - name: 'local'
                  value: 'test2'


            - renamed: 'should-become-present3'
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
            '''))

            input_items2 = yaml.safe_load(textwrap.dedent('''
            - renamed: 'should-become-present3'
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
            - first_index: 0
              id: 0
              renamed: should-stay-init
              options:
              - first_index: 0
                id: 0
                name: local
                state: present
                value: test
                weight: 0
              state: init
              weight: 0
            - first_index: 1
              id: 1
              renamed: should-become-present
              options:
              - first_index: 0
                id: 0
                name: local
                state: present
                value: test2
                weight: 0
              state: present
              weight: 0
            - first_index: 3
              id: 2
              renamed: should-become-present2
              options:
              - first_index: 0
                id: 0
                name: local
                state: present
                value: test2
                weight: 0
              state: present
              weight: 0
            - first_index: 5
              id: 3
              renamed: should-become-present3
              options:
              - comment: This comment should survive.
                first_index: 0
                id: 0
                name: local1
                options:
                - first_index: 0
                  id: 0
                  name: local2
                  state: present
                  value: test2
                  weight: 0
                state: present
                weight: 0
              - first_index: 1
                id: 1
                name: external1
                options:
                - first_index: 0
                  id: 0
                  name: external2
                  state: present
                  value: test
                  weight: 0
                state: present
                weight: 0
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items1, input_items2, name='renamed')

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_ignore_raw(self):
            input_items1 = yaml.safe_load(textwrap.dedent('''
            - name: 'test-item'
              options:

                - name: 'test-option'
                  raw: 'test-is-present'
                  state: 'present'
            '''))

            input_items2 = yaml.safe_load(textwrap.dedent('''
            - name: 'test-item'
              options:

                - name: 'test-option'
                  raw: 'test-is-ignored'
                  state: 'ignore'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: test-item
              options:
              - first_index: 0
                id: 0
                name: test-option
                state: present
                raw: test-is-present
                weight: 0
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items1, input_items2)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_anchor_to_before_in_zone(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'target'
              value: 'main'

            - name: 'before_item'
              anchor_to: 'target'
              weight: -1
              value: 'before'

            - name: 'after_item'
              anchor_to: 'target'
              weight: 1
              value: 'after'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - anchor_to: target
              first_index: 1
              id: 0
              name: before_item
              state: present
              value: before
              weight: -1
            - first_index: 0
              id: 1
              name: target
              state: present
              value: main
              weight: 0
            - anchor_to: target
              first_index: 2
              id: 2
              name: after_item
              state: present
              value: after
              weight: 1
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_alias(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              alias: 'local_alias'

            - name: 'other'
              option: 'other_option'

            - name: 'both'
              option: 'both_option'
              alias: 'both_alias'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - alias: local_alias
              first_index: 0
              id: 0
              name: local
              option: local_alias
              state: present
              weight: 0

            - alias: other_option
              first_index: 1
              id: 1
              name: other
              option: other_option
              state: present
              weight: 0

            - alias: both_alias
              first_index: 2
              id: 2
              name: both
              option: both_alias
              state: present
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_alias_nested(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              value:

                - name: 'element1'
                  alias: 'element1_alias'

                - name: 'element2'
                  option: 'element2_option'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              state: present
              value:

              - alias: element1_alias
                first_index: 0
                id: 0
                name: element1
                option: element1_alias
                state: present
                weight: 0

              - alias: element2_option
                first_index: 1
                id: 1
                name: element2
                option: element2_option
                state: present
                weight: 0
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_alias(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              alias: 'local_alias'

            - name: 'other'
              option: 'other_option'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - alias: local_alias
              first_index: 0
              id: 0
              name: local
              option: local_alias
              state: present
              weight: 0

            - alias: other_option
              first_index: 1
              id: 1
              name: other
              option: other_option
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_alias_nested(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              options:

                - name: 'element1'
                  alias: 'element1_alias'

                - name: 'element2'
                  option: 'element2_option'

                - name: 'element3'
                  option: 'both_option'
                  alias: 'both_alias'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              options:

              - alias: element1_alias
                first_index: 0
                id: 0
                name: element1
                option: element1_alias
                state: present
                weight: 0

              - alias: element2_option
                first_index: 1
                id: 1
                name: element2
                option: element2_option
                state: present
                weight: 0

              - alias: both_alias
                first_index: 2
                id: 2
                name: element3
                option: both_alias
                state: present
                weight: 0
              state: present
              weight: 0
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_separator(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              separator: True
              value: 'test'

            - name: 'local2'
              value: 'test2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              separator: true
              state: present
              value: test
              weight: 0

            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_items_separator(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              separator: True
              value: 'test'

            - name: 'local2'
              value: 'test2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              separator: true
              state: present
              value: test
              weight: 0

            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_items(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_section(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - name: 'local'
              section: 'base'
              value: 'test'

            - name: 'local2'
              value: 'test2'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: local
              section: base
              state: present
              value: test
              weight: 0

            - first_index: 1
              id: 1
              name: local2
              state: present
              value: test2
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

        def test_parse_kv_config_section_raw(self):
            input_items = yaml.safe_load(textwrap.dedent('''
            - section: 'base'
            '''))

            expected_items = yaml.safe_load(textwrap.dedent('''
            - first_index: 0
              id: 0
              name: section
              state: present
              value: base
              weight: 0
            '''))

            items = parse_kv_config(input_items)

            self.assertEqual(items, expected_items)

    unittest.main()
