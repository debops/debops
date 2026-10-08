# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the DebOps inventory file specification.

Written with 'unittest' so that the suite runs without extra dependencies:

    PYTHONPATH=src python3 -m unittest discover -s src/tests
"""

from debops.exceptions import InventorySpecError
from debops.inventoryspec import (parse_spec, merge_specs, resolve_paths,
                                  apply_spec, render_spec, render_keep,
                                  resolve_keep, load_template,
                                  DEFAULT_VERSION, PATH_RENDERED_VERSIONS,
                                  CONTENT_RENDERED_VERSIONS, SPEC_TEMPLATES,
                                  SPEC_VERSION)
from unittest import mock
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import yaml


class ParseSpecTestCase(unittest.TestCase):
    """Validation of the document itself."""

    def test_minimal_document(self):
        spec = parse_spec('---\nfiles:\n  hosts: "[all]"\n')

        # An unversioned document is a version 0 document, which is written
        # exactly as it is
        self.assertEqual(spec['version'], DEFAULT_VERSION)
        self.assertEqual(DEFAULT_VERSION, 0)

        # A plain scalar has no trailing newline, a literal block does; the
        # contents are stored exactly as YAML reads them
        self.assertEqual(spec['files'], {'hosts': '[all]'})

    def test_literal_block_keeps_trailing_newline(self):
        spec = parse_spec('---\nfiles:\n  hosts: |\n    [all]\n')

        self.assertEqual(spec['files'], {'hosts': '[all]\n'})

    def test_current_version_accepted(self):
        spec = parse_spec('---\nversion: 3\nfiles:\n  hosts: x\n')

        self.assertEqual(spec['version'], 3)
        self.assertEqual(spec['files'], {'hosts': 'x'})

    def test_every_known_version_accepted(self):
        for version in range(0, 4):
            spec = parse_spec('---\nversion: {}\nfiles:\n  hosts: x\n'
                              .format(version))

            self.assertEqual(spec['version'], version)

    def test_negative_version_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nversion: -1\nfiles:\n  hosts: x\n')

        self.assertIn('version -1', str(cm.exception))

    def test_version_render_levels_are_monotonic(self):
        # Each version adds one thing to the previous one: templated paths,
        # templated contents, then the pipe() and include() globals
        self.assertEqual(PATH_RENDERED_VERSIONS, (1, 2, 3))
        self.assertEqual(CONTENT_RENDERED_VERSIONS, (2, 3))

    def test_newer_version_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nversion: 4\nfiles:\n  hosts: x\n')

        self.assertIn('version 4', str(cm.exception))
        self.assertIn('understands version 3', str(cm.exception))

    def test_non_numeric_version_rejected(self):
        with self.assertRaises(InventorySpecError):
            parse_spec('---\nversion: one\nfiles:\n  hosts: x\n')

    def test_unknown_top_level_key_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles:\n  hosts: x\nextra: 1\n')

        self.assertIn('"extra"', str(cm.exception))

    def test_missing_files_key_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nversion: 2\n')

        self.assertIn('No "files" key', str(cm.exception))

    def test_files_must_be_a_mapping(self):
        with self.assertRaises(InventorySpecError):
            parse_spec('---\nfiles: hello\n')

    def test_empty_document_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('')

        self.assertIn('must be a YAML dictionary', str(cm.exception))

    def test_non_string_content_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles:\n  hosts: 42\n')

        self.assertIn('must be a text block', str(cm.exception))

    def test_empty_path_rejected(self):
        with self.assertRaises(InventorySpecError):
            parse_spec('---\nfiles:\n  "  ": x\n')

    def test_invalid_yaml_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('files:\n  hosts: "unterminated\n')

        self.assertIn('Invalid YAML', str(cm.exception))

    def test_duplicate_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles:\n  hosts: first\n  hosts: second\n')

        self.assertIn('duplicate key', str(cm.exception))

    def test_contents_are_not_expanded(self):
        spec = parse_spec('---\nfiles:\n  hosts: "$HOME and $PATH"\n')

        self.assertEqual(spec['files'], {'hosts': '$HOME and $PATH'})

    def test_null_content_is_a_removal(self):
        spec = parse_spec('---\nfiles:\n  group_vars/: null\n')

        self.assertIsNone(spec['files']['group_vars/'])

    def test_empty_directory_value_is_allowed(self):
        spec = parse_spec("---\nfiles:\n  group_vars/: ''\n")

        self.assertEqual(spec['files']['group_vars/'], '')

    def test_directory_with_contents_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles:\n  group_vars/: "a: 1"\n')

        self.assertIn('cannot have file contents', str(cm.exception))


class RenderPathsTestCase(unittest.TestCase):
    """Rendering of the paths of a version 1 document.

    A version 1 document has its paths rendered and its contents left alone,
    which is the middle level between version 0 (nothing is rendered) and
    version 2 (everything is).
    """

    def setUp(self):
        self.context = {'hostname': 'example.org', 'fqdn': 'host.example.org'}

    def render(self, files, context=None, **kwargs):
        kwargs.setdefault('version', 1)
        kwargs.setdefault('render_contents', False)

        return render_spec(files, self.context if context is None else context,
                           'doc.yml', **kwargs)

    def test_path_is_rendered(self):
        files = self.render({'host_vars/{{ hostname }}/main.yml': 'x\n'})

        self.assertEqual(files, {'host_vars/example.org/main.yml': 'x\n'})

    def test_contents_are_left_alone(self):
        files = self.render({'hosts': '{{ ansible_domain }}\n'})

        self.assertEqual(files, {'hosts': '{{ ansible_domain }}\n'})

    def test_removal_path_is_rendered(self):
        files = self.render({'host_vars/{{ hostname }}/': None})

        self.assertEqual(files, {'host_vars/example.org/': None})

    def test_environment_variable_in_path(self):
        context = dict(self.context, env={'TARGET': 'web1'})

        files = self.render({'host_vars/{{ env.TARGET }}/main.yml': 'x\n'},
                            context=context)

        self.assertEqual(files, {'host_vars/web1/main.yml': 'x\n'})

    def test_undefined_variable_in_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render({'host_vars/{{ nope }}/main.yml': 'x\n'})

        self.assertIn('doc.yml', str(cm.exception))

    def test_empty_rendered_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render({'{{ "" }}': 'x\n'})

        self.assertIn('empty', str(cm.exception))

    def test_paths_rendered_to_the_same_file_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render({'host_vars/{{ hostname }}.yml': 'a\n',
                         'host_vars/example.org.yml': 'b\n'})

        self.assertIn('same file', str(cm.exception))

    def test_pipe_is_not_available(self):
        # Running a command stays a version 3 privilege, so a path cannot
        # execute anything even when --allow-io was given
        with self.assertRaises(InventorySpecError) as cm:
            self.render({'{{ pipe("id -un") }}': 'x\n'}, allow_io=True)

        self.assertIn('version 3', str(cm.exception))

    def test_include_is_not_available(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render({'{{ include("/etc/passwd") }}': 'x\n'}, allow_io=True)

        self.assertIn('version 3', str(cm.exception))

    def test_rendered_path_escape_is_caught_before_writing(self):
        files = self.render({'{{ "../../etc/passwd" }}': 'x\n'})

        base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, base_dir, True)

        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths(files, base_dir)

        self.assertIn('points outside', str(cm.exception))


class RenderSpecTestCase(unittest.TestCase):
    """Rendering of version 2 documents."""

    def setUp(self):
        self.context = {'hostname': 'example.org', 'fqdn': 'host.example.org'}

    def test_variable_is_substituted(self):
        files = render_spec({'hosts': '{{ hostname }}\n'}, self.context, 'x')

        self.assertEqual(files, {'hosts': 'example.org\n'})

    def test_escaped_delimiters_reach_the_file_verbatim(self):
        content = "{{ '{{' }} hostname {{ '}}' }}\n"

        files = render_spec({'hosts': content}, self.context, 'x')

        self.assertEqual(files, {'hosts': '{{ hostname }}\n'})

    def test_raw_block_is_kept_verbatim(self):
        content = '{% raw %}{{ ansible_domain }}{% endraw %}\n'

        files = render_spec({'hosts': content}, self.context, 'x')

        self.assertEqual(files, {'hosts': '{{ ansible_domain }}\n'})

    def test_trailing_newline_is_kept(self):
        files = render_spec({'hosts': 'line\n'}, self.context, 'x')

        self.assertTrue(files['hosts'].endswith('\n'))

    def test_undefined_variable_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            render_spec({'hosts': '{{ nope }}\n'}, self.context, 'doc.yml')

        self.assertIn('doc.yml', str(cm.exception))

    def test_syntax_error_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            render_spec({'hosts': '{% if %}\n'}, self.context, 'doc.yml')

        self.assertIn('doc.yml', str(cm.exception))

    def test_removal_passes_through(self):
        files = render_spec({'group_vars/': None}, self.context, 'doc.yml')

        self.assertIsNone(files['group_vars/'])

    def test_path_is_rendered(self):
        files = render_spec({'host_vars/{{ hostname }}/main.yml': 'x\n'},
                            self.context, 'doc.yml')

        self.assertEqual(files, {'host_vars/example.org/main.yml': 'x\n'})

    def test_removal_path_is_rendered(self):
        files = render_spec({'host_vars/{{ hostname }}/': None},
                            self.context, 'doc.yml')

        self.assertEqual(files, {'host_vars/example.org/': None})

    def test_environment_variable_in_path(self):
        context = dict(self.context, env={'TARGET': 'web1'})

        files = render_spec({'host_vars/{{ env.TARGET }}/main.yml': 'x\n'},
                            context, 'doc.yml')

        self.assertEqual(files, {'host_vars/web1/main.yml': 'x\n'})

    def test_undefined_variable_in_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            render_spec({'host_vars/{{ nope }}/main.yml': 'x\n'},
                        self.context, 'doc.yml')

        self.assertIn('doc.yml', str(cm.exception))

    def test_paths_rendered_to_the_same_file_rejected(self):
        files = {'host_vars/{{ hostname }}.yml': 'a\n',
                 'host_vars/example.org.yml': 'b\n'}

        with self.assertRaises(InventorySpecError) as cm:
            render_spec(files, self.context, 'doc.yml')

        self.assertIn('same file', str(cm.exception))

    def test_unrendered_paths_keep_their_key(self):
        files = render_spec({'host_vars/{{ hostname }}/': ''}, self.context,
                            'doc.yml', version=1, render_paths=False,
                            render_contents=False)

        self.assertEqual(files, {'host_vars/{{ hostname }}/': ''})

    def test_empty_rendered_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            render_spec({'{{ "" }}': 'x\n'}, self.context, 'doc.yml')

        self.assertIn('empty', str(cm.exception))

    def test_rendered_path_escape_is_caught_before_writing(self):
        files = render_spec({'{{ "../../etc/passwd" }}': 'x\n'},
                            self.context, 'doc.yml')

        base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, base_dir, True)

        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths(files, base_dir)

        self.assertIn('points outside', str(cm.exception))


class RenderKeepTestCase(unittest.TestCase):
    """Rendering of the 'keep' patterns."""

    def setUp(self):
        self.context = {'hostname': 'example.org', 'view': 'webservers'}

    def test_patterns_are_templated_in_version_2(self):
        keep = render_keep(['{{ view }}/custom.yml'], self.context, 'x',
                           version=2)

        self.assertEqual(keep, ['webservers/custom.yml'])

    def test_patterns_are_literal_in_version_0(self):
        keep = render_keep(['{{ view }}/custom.yml'], self.context, 'x',
                           version=0)

        self.assertEqual(keep, ['{{ view }}/custom.yml'])

    def test_patterns_are_templated_in_version_3(self):
        keep = render_keep(['{{ view }}/*.yml'], self.context, 'x', version=3)

        self.assertEqual(keep, ['webservers/*.yml'])

    def test_empty_list_stays_empty(self):
        for version in (0, 1, 2, 3):
            with self.subTest(version=version):
                self.assertEqual(render_keep([], self.context, 'x',
                                             version=version), [])

    def test_missing_variable_is_refused(self):
        with self.assertRaises(InventorySpecError) as cm:
            render_keep(['{{ nope }}/x.yml'], self.context, 'x', version=2)

        self.assertIn('nope', str(cm.exception))

    def test_globals_are_not_available(self):
        # Keeping a path is not an operation which reads or runs anything, so
        # a pattern must not be able to reach the specification
        with self.assertRaises(InventorySpecError):
            render_keep(["{{ pipe('id') }}"], self.context, 'x', version=3)


class PipeTestCase(unittest.TestCase):
    """The pipe() global of a version 3 document."""

    def render(self, content, version=3, allow_io=True):
        return render_spec({'file.yml': content}, {}, 'doc.yml',
                           version=version, allow_io=allow_io)['file.yml']

    @mock.patch('debops.inventoryspec._execute_command')
    def test_output_is_returned_without_trailing_newline(self, execute):
        execute.return_value = mock.Mock(returncode=0, stdout='key\n',
                                         stderr='')

        self.assertEqual(self.render('{{ pipe("echo key") }}\n'), 'key\n')

    @mock.patch('debops.inventoryspec._execute_command')
    def test_result_is_memoized(self, execute):
        execute.return_value = mock.Mock(returncode=0, stdout='x\n',
                                         stderr='')

        result = self.render('{{ pipe("cmd") }}{{ pipe("cmd") }}\n')

        self.assertEqual(result, 'xx\n')
        execute.assert_called_once()

    def test_command_requires_version_three(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ pipe("cmd") }}\n', version=2)

        self.assertIn('requires inventory specification version 3',
                      str(cm.exception))

    def test_command_requires_allow_io(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ pipe("cmd") }}\n', allow_io=False)

        self.assertIn('--allow-io', str(cm.exception))

    @mock.patch('debops.inventoryspec._execute_command')
    def test_failed_command_is_reported(self, execute):
        execute.return_value = mock.Mock(returncode=2, stdout='',
                                         stderr='no agent\n')

        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ pipe("ssh-add -L") }}\n')

        self.assertIn('exit code 2', str(cm.exception))
        self.assertIn('no agent', str(cm.exception))

    @mock.patch('debops.inventoryspec._execute_command')
    def test_timeout_is_reported(self, execute):
        execute.side_effect = subprocess.TimeoutExpired('cmd', 30)

        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ pipe("sleep 60") }}\n')

        self.assertIn('timed out', str(cm.exception))

    @mock.patch('debops.inventoryspec._execute_command')
    def test_empty_command_rejected(self, execute):
        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ pipe("  ") }}\n')

        self.assertIn('non-empty command', str(cm.exception))
        execute.assert_not_called()


class IncludeTestCase(unittest.TestCase):
    """The include() global of a version 3 document."""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)

    def write(self, name, content):
        path = os.path.join(self.base_dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as fh:
            fh.write(content)
        return path

    def render(self, content, version=3, allow_io=True):
        return render_spec({'file.yml': content}, {}, 'doc.yml',
                           version=version, allow_io=allow_io,
                           include_base=self.base_dir)['file.yml']

    def test_contents_are_included_verbatim(self):
        self.write('snippet.yml', '---\nkey: value\n')

        self.assertEqual(self.render('{{ include("snippet.yml") }}'),
                         '---\nkey: value\n')

    def test_included_jinja_is_not_rendered(self):
        self.write('snippet.yml', '{{ not_rendered }}\n')

        self.assertEqual(self.render('{{ include("snippet.yml") }}'),
                         '{{ not_rendered }}\n')

    def test_relative_path_uses_include_base(self):
        self.write(os.path.join('group_vars', 'all', 'x.yml'), 'a: 1\n')

        self.assertEqual(
            self.render('{{ include("group_vars/all/x.yml") }}'), 'a: 1\n')

    def test_environment_variables_are_expanded(self):
        self.write('x.yml', 'hello\n')
        os.environ['DEBOPS_TEST_INCLUDE'] = self.base_dir
        self.addCleanup(os.environ.pop, 'DEBOPS_TEST_INCLUDE', None)

        self.assertEqual(
            self.render('{{ include("$DEBOPS_TEST_INCLUDE/x.yml") }}'),
            'hello\n')

    def test_file_is_read_once(self):
        self.write('x.yml', 'hello\n')
        real_open = open

        with mock.patch('builtins.open', wraps=real_open) as opener:
            result = self.render(
                '{{ include("x.yml") }}{{ include("x.yml") }}')

        self.assertEqual(result, 'hello\nhello\n')
        self.assertEqual(opener.call_count, 1)

    def test_missing_file_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ include("nope.yml") }}')

        self.assertIn('Cannot include', str(cm.exception))

    def test_directory_rejected(self):
        os.makedirs(os.path.join(self.base_dir, 'adir'))

        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ include("adir") }}')

        self.assertIn('directory', str(cm.exception))

    def test_include_requires_version_three(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ include("x") }}', version=2)

        self.assertIn('requires inventory specification version 3',
                      str(cm.exception))

    def test_include_requires_allow_io(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.render('{{ include("x") }}', allow_io=False)

        self.assertIn('--allow-io', str(cm.exception))


class MergeSpecsTestCase(unittest.TestCase):
    """Combining several documents."""

    def test_later_specification_wins(self):
        first = parse_spec('---\nfiles:\n  hosts: first\n  extra: kept\n')
        second = parse_spec('---\nfiles:\n  hosts: second\n')

        merged, _keep, notices = merge_specs(
            [('first', first), ('second', second)])

        self.assertEqual(merged, {'hosts': 'second', 'extra': 'kept'})
        self.assertEqual(len(notices), 1)
        self.assertIn('hosts', notices[0])
        self.assertIn('second', notices[0])

    def test_no_notices_without_overlap(self):
        first = parse_spec('---\nfiles:\n  a: x\n')
        second = parse_spec('---\nfiles:\n  b: y\n')

        merged, _keep, notices = merge_specs(
            [('first', first), ('second', second)])

        self.assertEqual(merged, {'a': 'x', 'b': 'y'})
        self.assertEqual(notices, [])

    def test_kept_paths_are_unioned(self):
        first = parse_spec('---\nfiles: {}\nkeep: [a.yml]\n')
        second = parse_spec('---\nfiles: {}\nkeep: [b.yml]\n')

        _merged, keep, _notices = merge_specs(
            [('first', first), ('second', second)])

        # A document cannot drop the protection another one asked for
        self.assertEqual(keep, ['a.yml', 'b.yml'])

    def test_a_document_which_also_writes_a_kept_path_is_refused(self):
        first = parse_spec('---\nfiles: {}\nkeep: ["group_vars/*.yml"]\n')
        second = parse_spec('---\nfiles:\n  group_vars/all/nginx.yml: x\n')

        with self.assertRaises(InventorySpecError) as cm:
            merge_specs([('first', first), ('second', second)])

        self.assertIn('group_vars/all/nginx.yml', str(cm.exception))
        self.assertIn('keep', str(cm.exception))

    def test_keeping_a_path_which_nothing_writes_is_fine(self):
        first = parse_spec('---\nfiles: {}\nkeep: [group_vars/all/old.yml]\n')
        second = parse_spec('---\nfiles:\n  group_vars/all/new.yml: x\n')

        merged, keep, notices = merge_specs(
            [('first', first), ('second', second)])

        self.assertEqual(merged, {'group_vars/all/new.yml': 'x'})
        self.assertEqual(keep, ['group_vars/all/old.yml'])
        self.assertEqual(notices, [])

    def test_removing_a_kept_path_is_a_contradiction_too(self):
        first = parse_spec('---\nfiles: {}\nkeep: [group_vars/all/x.yml]\n')
        second = parse_spec('---\nfiles:\n  group_vars/all/x.yml: null\n')

        with self.assertRaises(InventorySpecError) as cm:
            merge_specs([('first', first), ('second', second)])

        self.assertIn('contradicts itself', str(cm.exception))

    def test_the_conflict_is_found_through_an_environment_variable(self):
        os.environ['DEBOPS_TEST_VIEW'] = 'webservers'
        self.addCleanup(os.environ.pop, 'DEBOPS_TEST_VIEW', None)

        first = parse_spec('---\nfiles: {}\nkeep: [webservers/x.yml]\n')
        second = parse_spec('---\nfiles:\n  $DEBOPS_TEST_VIEW/x.yml: x\n')

        with self.assertRaises(InventorySpecError):
            merge_specs([('first', first), ('second', second)])


class ParseKeepTestCase(unittest.TestCase):
    """The 'keep' key of a document."""

    def test_keep_is_optional(self):
        self.assertEqual(parse_spec('---\nfiles: {}\n')['keep'], [])

    def test_keep_is_a_list_of_patterns(self):
        spec = parse_spec('---\nfiles: {}\nkeep: [a.yml, "group_vars/*"]\n')

        self.assertEqual(spec['keep'], ['a.yml', 'group_vars/*'])

    def test_keep_must_be_a_list(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles: {}\nkeep: a.yml\n')

        self.assertIn('list', str(cm.exception))

    def test_keep_entry_must_be_a_string(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles: {}\nkeep: [[a.yml]]\n')

        self.assertIn('string', str(cm.exception))

    def test_empty_keep_entry_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            parse_spec('---\nfiles: {}\nkeep: [" "]\n')

        self.assertIn('Empty path', str(cm.exception))


class ResolveKeepTestCase(unittest.TestCase):
    """Validation and matching of the 'keep' patterns."""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)

    def keeps(self, *patterns):
        return resolve_keep(list(patterns), self.base_dir)

    def target(self, *parts):
        return os.path.join(self.base_dir, *parts)

    def test_exact_path_is_kept(self):
        keeps = self.keeps('group_vars/all/keyring.yml')

        self.assertTrue(keeps(self.target('group_vars', 'all',
                                          'keyring.yml')))
        self.assertFalse(keeps(self.target('group_vars', 'all', 'nginx.yml')))

    def test_kept_directory_protects_its_contents(self):
        keeps = self.keeps('group_vars/all/')

        self.assertTrue(keeps(self.target('group_vars', 'all', 'keyring.yml')))
        self.assertTrue(keeps(self.target('group_vars', 'all')))
        self.assertFalse(keeps(self.target('group_vars', 'web', 'x.yml')))

    def test_star_crosses_the_path_separator(self):
        # fnmatch semantics: '*.yml' reaches a file at any depth, which keeps
        # more than a path-by-path reading would, never less
        keeps = self.keeps('*.yml')

        self.assertTrue(keeps(self.target('group_vars', 'all', 'keyring.yml')))
        self.assertFalse(keeps(self.target('group_vars', 'all', 'x.conf')))

    def test_star_within_one_directory(self):
        keeps = self.keeps('group_vars/all/*.yml')

        self.assertTrue(keeps(self.target('group_vars', 'all', 'keyring.yml')))
        self.assertFalse(keeps(self.target('group_vars', 'web', 'x.yml')))

    def test_matching_is_case_sensitive(self):
        keeps = self.keeps('group_vars/all/Keyring.yml')

        self.assertFalse(keeps(self.target('group_vars', 'all',
                                           'keyring.yml')))

    def test_nothing_is_kept_by_default(self):
        keeps = self.keeps()

        self.assertFalse(keeps(self.target('group_vars', 'all', 'x.yml')))

    def test_matching_does_not_look_at_the_filesystem(self):
        # Nothing has been created in the temporary directory, so a pattern
        # which names a path that does not exist is matched on the name alone
        # rather than reported as an error
        keeps = self.keeps('group_vars/never/existed.yml')

        self.assertTrue(keeps(self.target('group_vars', 'never',
                                          'existed.yml')))
        self.assertFalse(keeps(self.target('group_vars', 'never',
                                           'other.yml')))

    def test_environment_variables_are_expanded(self):
        os.environ['DEBOPS_TEST_VIEW'] = 'webservers'
        self.addCleanup(os.environ.pop, 'DEBOPS_TEST_VIEW', None)

        keeps = self.keeps('group_vars/$DEBOPS_TEST_VIEW/x.yml')

        self.assertTrue(keeps(self.target('group_vars', 'webservers', 'x.yml')))

    def test_absolute_pattern_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.keeps('/etc/passwd')

        self.assertIn('relative', str(cm.exception))

    def test_parent_pattern_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.keeps('../outside/x.yml')

        self.assertIn('..', str(cm.exception))

    def test_tilde_pattern_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.keeps('~/x.yml')

        self.assertIn('~', str(cm.exception))

    def test_pattern_which_names_no_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            self.keeps('.')

        self.assertIn('does not name a path', str(cm.exception))


class ResolvePathsTestCase(unittest.TestCase):

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)

    def test_relative_paths_are_mapped_under_base_dir(self):
        resolved = resolve_paths({'group_vars/all/x.yml': 'v'}, self.base_dir)

        self.assertEqual(list(resolved),
                         [os.path.join(self.base_dir, 'group_vars/all/x.yml')])

    def test_environment_variables_expanded_in_paths(self):
        os.environ['DEBOPS_TEST_VIEW'] = 'webservers'
        self.addCleanup(os.environ.pop, 'DEBOPS_TEST_VIEW', None)

        resolved = resolve_paths({'group_vars/$DEBOPS_TEST_VIEW/nginx.yml':
                                  'v'}, self.base_dir)

        self.assertEqual(list(resolved),
                         [os.path.join(self.base_dir,
                                       'group_vars/webservers/nginx.yml')])

    def test_absolute_path_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths({'/etc/passwd': 'v'}, self.base_dir)

        self.assertIn('must be relative', str(cm.exception))

    def test_tilde_path_rejected(self):
        with self.assertRaises(InventorySpecError):
            resolve_paths({'~/escape': 'v'}, self.base_dir)

    def test_traversal_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths({'../escape': 'v'}, self.base_dir)

        self.assertIn('points outside', str(cm.exception))

    def test_traversal_through_directory_rejected(self):
        with self.assertRaises(InventorySpecError):
            resolve_paths({'group_vars/../../escape': 'v'}, self.base_dir)

    def test_symlink_escape_rejected(self):
        outside = tempfile.mkdtemp(prefix='debops-spec-outside-')
        self.addCleanup(shutil.rmtree, outside, True)

        os.symlink(outside, os.path.join(self.base_dir, 'link'))

        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths({'link/escape': 'v'}, self.base_dir)

        self.assertIn('points outside', str(cm.exception))

    def test_colliding_paths_rejected(self):
        os.environ['DEBOPS_TEST_ALIAS'] = 'webservers'
        self.addCleanup(os.environ.pop, 'DEBOPS_TEST_ALIAS', None)

        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths({'group_vars/webservers/x.yml': 'a',
                           'group_vars/$DEBOPS_TEST_ALIAS/x.yml': 'b'},
                          self.base_dir)

        self.assertIn('resolve to the same file', str(cm.exception))

    def test_directory_path_is_marked(self):
        resolved = resolve_paths({'group_vars/': None}, self.base_dir)
        entry = list(resolved.values())[0]

        self.assertTrue(entry.is_dir)
        self.assertIsNone(entry.content)
        self.assertEqual(entry.path,
                         os.path.join(self.base_dir, 'group_vars'))

    def test_directory_trailing_separator_is_stripped(self):
        resolved = resolve_paths({'group_vars//': ''}, self.base_dir)
        entry = list(resolved.values())[0]

        self.assertTrue(entry.is_dir)
        self.assertEqual(entry.content, '')
        self.assertEqual(entry.path,
                         os.path.join(self.base_dir, 'group_vars'))

    def test_inventory_directory_itself_rejected(self):
        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths({'.': None}, self.base_dir)

        self.assertIn('the Ansible inventory directory itself',
                      str(cm.exception))

    def test_directory_with_contents_from_expansion_rejected(self):
        os.environ['DEBOPS_TEST_DIR'] = 'group_vars/'
        self.addCleanup(os.environ.pop, 'DEBOPS_TEST_DIR', None)

        with self.assertRaises(InventorySpecError) as cm:
            resolve_paths({'$DEBOPS_TEST_DIR': 'a: 1\n'}, self.base_dir)

        self.assertIn('cannot have file contents', str(cm.exception))


class ApplySpecTestCase(unittest.TestCase):

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)

        self.files = {'hosts': '[webservers]\nweb1\n',
                      'group_vars/webservers/nginx.yml': 'a: 1\n'}

    def read(self, relative_path):
        with open(os.path.join(self.base_dir, relative_path), 'r') as fh:
            return fh.read()

    def test_files_are_written(self):
        result = apply_spec(self.files, self.base_dir)

        self.assertEqual(self.read('hosts'), '[webservers]\nweb1\n')
        self.assertEqual(self.read('group_vars/webservers/nginx.yml'), 'a: 1\n')
        self.assertEqual(len(result['written']), 2)
        self.assertEqual(result['skipped'], [])

    def test_pre_existing_files_are_skipped(self):
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('mine\n')

        pre_existing = {os.path.join(self.base_dir, 'hosts')}
        result = apply_spec(self.files, self.base_dir,
                            pre_existing=pre_existing)

        self.assertEqual(self.read('hosts'), 'mine\n')
        self.assertEqual(result['skipped'],
                         [os.path.join(self.base_dir, 'hosts')])
        self.assertEqual(len(result['written']), 1)

    def test_files_generated_in_the_same_run_are_overwritten(self):
        # 'hosts' exists but was not in pre_existing, so it was created by
        # DebOps during this command and the specification may replace it
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('generated by debops\n')

        apply_spec(self.files, self.base_dir, pre_existing=set())

        self.assertEqual(self.read('hosts'), '[webservers]\nweb1\n')

    def test_overwrite_replaces_pre_existing_files(self):
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('mine\n')

        pre_existing = {os.path.join(self.base_dir, 'hosts')}
        apply_spec(self.files, self.base_dir, pre_existing=pre_existing,
                   overwrite=True)

        self.assertEqual(self.read('hosts'), '[webservers]\nweb1\n')

    def test_dry_run_writes_nothing(self):
        result = apply_spec(self.files, self.base_dir, dry_run=True)

        self.assertEqual(len(result['planned']), 2)
        self.assertEqual(result['written'], [])
        self.assertFalse(os.path.exists(os.path.join(self.base_dir, 'hosts')))

    def test_empty_file_is_written(self):
        apply_spec({'hosts': ''}, self.base_dir)

        self.assertEqual(self.read('hosts'), '')

    def test_file_is_removed(self):
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('mine\n')

        result = apply_spec({'hosts': None}, self.base_dir)

        self.assertFalse(os.path.exists(os.path.join(self.base_dir, 'hosts')))
        self.assertEqual(result['removed'],
                         [os.path.join(self.base_dir, 'hosts')])

    def test_missing_removal_is_a_no_op(self):
        result = apply_spec({'hosts': None}, self.base_dir)

        self.assertEqual(result['removed'], [])
        self.assertEqual(result['skipped'], [])

    def test_directory_is_removed_recursively(self):
        os.makedirs(os.path.join(self.base_dir, 'group_vars', 'all'))
        with open(os.path.join(self.base_dir, 'group_vars', 'all', 'x.yml'),
                  'w') as fh:
            fh.write('a: 1\n')

        apply_spec({'group_vars/': None}, self.base_dir)

        self.assertFalse(os.path.exists(os.path.join(self.base_dir,
                                                     'group_vars')))

    def test_empty_directory_clears_existing_contents(self):
        os.makedirs(os.path.join(self.base_dir, 'host_vars'))
        with open(os.path.join(self.base_dir, 'host_vars', 'web1.yml'),
                  'w') as fh:
            fh.write('a: 1\n')

        apply_spec({'host_vars/': ''}, self.base_dir)

        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'host_vars')))
        self.assertEqual(os.listdir(os.path.join(self.base_dir, 'host_vars')),
                         [])

    def test_empty_directory_is_created(self):
        apply_spec({'host_vars/': ''}, self.base_dir)

        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'host_vars')))

    def test_pre_existing_file_is_not_removed(self):
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('mine\n')

        pre_existing = {os.path.join(self.base_dir, 'hosts')}
        result = apply_spec({'hosts': None}, self.base_dir,
                            pre_existing=pre_existing)

        self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'hosts')))
        self.assertEqual(result['skipped'],
                         [os.path.join(self.base_dir, 'hosts')])

    def test_overwrite_removes_pre_existing_file(self):
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('mine\n')

        pre_existing = {os.path.join(self.base_dir, 'hosts')}
        apply_spec({'hosts': None}, self.base_dir,
                   pre_existing=pre_existing, overwrite=True)

        self.assertFalse(os.path.exists(os.path.join(self.base_dir, 'hosts')))

    def test_dry_run_removal_writes_nothing(self):
        with open(os.path.join(self.base_dir, 'hosts'), 'w') as fh:
            fh.write('mine\n')

        result = apply_spec({'hosts': None}, self.base_dir, dry_run=True)

        self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'hosts')))
        self.assertEqual(result['planned_removed'],
                         [os.path.join(self.base_dir, 'hosts')])

    def test_symlink_removal_is_refused(self):
        target = os.path.join(self.base_dir, 'real')
        with open(target, 'w') as fh:
            fh.write('x\n')
        os.symlink(target, os.path.join(self.base_dir, 'link'))

        with self.assertRaises(InventorySpecError) as cm:
            apply_spec({'link': None}, self.base_dir)

        self.assertIn('symbolic link', str(cm.exception))
        self.assertTrue(os.path.islink(os.path.join(self.base_dir, 'link')))

    def test_symlink_inside_removed_directory_is_refused(self):
        os.makedirs(os.path.join(self.base_dir, 'group_vars', 'all'))
        os.symlink('/etc/hostname',
                   os.path.join(self.base_dir, 'group_vars', 'all', 'link'))

        with self.assertRaises(InventorySpecError) as cm:
            apply_spec({'group_vars/': None}, self.base_dir)

        self.assertIn('symbolic link', str(cm.exception))
        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'group_vars')))

    def test_symlink_write_is_refused(self):
        target = os.path.join(self.base_dir, 'real')
        os.makedirs(target)
        os.symlink(target, os.path.join(self.base_dir, 'link'))

        with self.assertRaises(InventorySpecError) as cm:
            apply_spec({'link/x.yml': 'a: 1\n'}, self.base_dir)

        self.assertIn('symbolic link', str(cm.exception))


class ApplySpecKeepTestCase(unittest.TestCase):
    """The 'keep' patterns passed to apply_spec()."""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='debops-spec-test-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)

        self.keyring = os.path.join(self.base_dir, 'group_vars', 'all',
                                    'keyring.yml')
        os.makedirs(os.path.dirname(self.keyring))
        self.write(self.keyring, 'seedvault: unchanged\n')
        self.write(os.path.join(self.base_dir, 'group_vars', 'all',
                                'nginx.yml'), 'mine: unchanged\n')

    def write(self, path, contents):
        with open(path, 'w') as fh:
            fh.write(contents)

    def read(self, path):
        with open(path, 'r') as fh:
            return fh.read()

    def test_kept_file_is_not_removed(self):
        result = apply_spec({'group_vars/all/keyring.yml': None}, self.base_dir,
                            keep=['group_vars/all/keyring.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertEqual(result['removed'], [])
        self.assertEqual(result['kept'], [self.keyring])

    def test_kept_file_wins_over_force(self):
        result = apply_spec({'group_vars/all/keyring.yml': None}, self.base_dir,
                            overwrite=True, keep=['group_vars/all/keyring.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertEqual(result['removed'], [])
        self.assertEqual(result['kept'], [self.keyring])

    def test_kept_directory_protects_the_directory_and_its_contents(self):
        result = apply_spec({'group_vars/': ''}, self.base_dir,
                            keep=['group_vars/all'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'group_vars', 'all')))
        self.assertEqual(result['removed'], [])
        # A kept directory keeps every path below it, including the files which
        # no pattern names
        self.assertEqual(result['kept'],
                         sorted([os.path.join(self.base_dir, 'group_vars',
                                              'all'),
                                 self.keyring,
                                 os.path.join(self.base_dir, 'group_vars',
                                              'all', 'nginx.yml')]))

    def test_kept_directory_protects_a_file_which_no_pattern_names(self):
        # 'group_vars/all/*.yml' does not name 'group_vars' itself, but the
        # kept files below it keep the directory above them alive
        result = apply_spec({'group_vars/': ''}, self.base_dir,
                            keep=['group_vars/all/*.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'group_vars', 'all')))
        self.assertEqual(result['removed'], [])

    def test_unkept_file_is_still_removed(self):
        nginx = os.path.join(self.base_dir, 'group_vars', 'all', 'nginx.yml')

        result = apply_spec({'group_vars/': ''}, self.base_dir,
                            keep=['group_vars/all/keyring.yml'])

        self.assertFalse(os.path.exists(nginx))
        self.assertIn(nginx, result['removed'])

    def test_dry_run_reports_the_kept_file_and_plans_the_others(self):
        nginx = os.path.join(self.base_dir, 'group_vars', 'all', 'nginx.yml')

        result = apply_spec({'group_vars/': ''}, self.base_dir, dry_run=True,
                            keep=['group_vars/all/keyring.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertEqual(self.read(nginx), 'mine: unchanged\n')
        self.assertEqual(result['removed'], [])
        self.assertEqual(result['kept'], [self.keyring])
        self.assertIn(nginx, result['planned_removed'])

    def test_dry_run_reports_a_directory_it_would_keep(self):
        result = apply_spec({'group_vars/': ''}, self.base_dir, dry_run=True,
                            keep=['group_vars/all'])

        self.assertEqual(result['planned_removed'], [])
        self.assertEqual(result['kept'],
                         sorted([os.path.join(self.base_dir, 'group_vars',
                                              'all'),
                                 self.keyring,
                                 os.path.join(self.base_dir, 'group_vars',
                                              'all', 'nginx.yml')]))

    def test_a_kept_path_is_left_alone_by_a_removal_of_its_directory(self):
        os.makedirs(os.path.join(self.base_dir, 'group_vars', 'web'))

        apply_spec({'group_vars/all': None}, self.base_dir, keep=[
            'group_vars/all/keyring.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')

    def test_removal_keeps_a_file_below_an_intermediate_directory(self):
        # The keep pattern names a file one directory below the removal
        # target, so the walk has to preserve both 'group_vars/all' and the
        # 'group_vars' directory itself
        result = apply_spec({'group_vars/': None}, self.base_dir, keep=[
            'group_vars/all/keyring.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'group_vars', 'all')))
        self.assertFalse(os.path.exists(os.path.join(
            self.base_dir, 'group_vars', 'all', 'nginx.yml')))

        # The directory which survived is reported as kept rather than
        # silently ignored
        self.assertEqual(result['kept'],
                         sorted([os.path.join(self.base_dir, 'group_vars'),
                                 self.keyring]))
        self.assertEqual(result['removed'],
                         [os.path.join(self.base_dir, 'group_vars', 'all',
                                       'nginx.yml')])

    def test_dry_run_keeps_a_file_below_an_intermediate_directory(self):
        result = apply_spec({'group_vars/': None}, self.base_dir,
                            dry_run=True, keep=[
                                'group_vars/all/keyring.yml'])

        self.assertTrue(os.path.isdir(os.path.join(self.base_dir,
                                                   'group_vars', 'all')))
        self.assertEqual(result['planned_removed'],
                         [os.path.join(self.base_dir, 'group_vars', 'all',
                                       'nginx.yml')])
        self.assertEqual(result['kept'],
                         sorted([os.path.join(self.base_dir, 'group_vars'),
                                 self.keyring]))
        self.assertNotIn(os.path.join(self.base_dir, 'group_vars'),
                         result['planned_removed'])

    def test_nothing_is_kept_without_patterns(self):
        result = apply_spec({'group_vars/': ''}, self.base_dir)

        self.assertEqual(result['kept'], [])
        self.assertFalse(os.path.exists(self.keyring))

    def test_a_kept_path_is_not_written_even_when_both_are_asked_for(self):
        # merge_specs() refuses this combination, so it only happens when the
        # mapping is assembled by the caller
        result = apply_spec({'group_vars/all/keyring.yml': 'replaced\n'},
                            self.base_dir,
                            keep=['group_vars/all/keyring.yml'])

        self.assertEqual(self.read(self.keyring), 'seedvault: unchanged\n')
        self.assertEqual(result['written'], [])
        self.assertEqual(result['kept'], [self.keyring])


GRAPH_OUTPUT = """\
@all:
  |--@ungrouped:
  |--@webservers:
  |  |--web1
  |  |  |--{ansible_host = 192.0.2.10}
  |  |  |--{nginx__server_name = example.org}
  |  |--{nginx__server_name = example.org}
  |--@staging_pool:
  |--{nginx__server_name = example.org}
"""

VARIABLE_OUTPUT = """\
@all:
  |--@webservers:
  |  |--web1
  |  |  |--{
  |  |  |    "keyring__local_path": "..."
  |  |  }
"""


