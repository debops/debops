# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .exceptions import InventorySpecError
from .utils import write_file
import collections
import collections.abc
import fnmatch
import jinja2
import os
import pkgutil
import subprocess
import yaml

# Highest version of the inventory file specification understood by this
# release; a document which declares a newer one is rejected.
SPEC_VERSION = 3

# Version assumed for a document which omits the 'version' key. Kept at the
# first version of the format on purpose, so that a document which does not ask
# for templating is written as it is.
DEFAULT_VERSION = 0

# Versions whose file paths are Jinja2 templates. Version 0 writes paths
# literally, so a path which happens to contain Jinja delimiters is left alone.
PATH_RENDERED_VERSIONS = (1, 2, 3)

# Versions whose file contents are Jinja2 templates instead of literal text.
# Version 0 and 1 write the contents as they are.
CONTENT_RENDERED_VERSIONS = (2, 3)

# Versions which may reach outside of the specification with the pipe() and
# include() globals.
IO_VERSIONS = (3,)

# How long a command run with pipe() may take before it is killed.
PIPE_TIMEOUT = 30

# Top-level keys recognized in an inventory specification document.
SPEC_KEYS = ('files', 'version', 'keep')

# Specifications shipped with the DebOps package, selected with the
# '--template' option. Kept as an explicit list because the package may be
# installed as a zip archive, where its data files cannot be listed at
# runtime.
SPEC_TEMPLATES = ('hosts', 'local', 'clear', 'sshkeys')

# Directory inside the package data which holds the shipped specifications.
TEMPLATE_DIR = os.path.join('_data', 'templates', 'inventoryspec')

# A resolved path entry. 'path' is the absolute path as it was written, without
# symbolic links resolved, so that a symlink can be detected before it is
# followed. 'content' is None for a removal, a string for a file. 'is_dir' is
# set for a path which ends in a separator.
ResolvedEntry = collections.namedtuple(
    'ResolvedEntry', ('path', 'content', 'is_dir'))


class StrictLoader(yaml.SafeLoader):
    """SafeLoader which rejects duplicate mapping keys.

    PyYAML silently keeps the value of the last of two identical keys. In a
    specification, where the whole document is a set of paths, that would hide
    a path which is defined twice.
    """

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)

        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)

            if not isinstance(key, collections.abc.Hashable):
                continue

            if key in seen:
                raise yaml.constructor.ConstructorError(
                    'while constructing a mapping', node.start_mark,
                    'found duplicate key "{}"'.format(key),
                    key_node.start_mark)

            seen.add(key)

        return super().construct_mapping(node, deep=deep)


def parse_spec(document, source='inventory specification'):
    """Parse and validate an inventory specification document.

    The document is a YAML mapping with an optional 'version' key, an optional
    'keep' list and a required 'files' mapping. Each key in 'files' is a path
    relative to the Ansible inventory directory, each value is the contents of
    the file to create. Environment variables are expanded in the paths later
    on, see :func:`resolve_paths`.

    'keep' lists paths which the document must not remove or clear; see
    :func:`resolve_keep`.

    The contents are returned as they are; a document whose version asks for
    templating must be run through :func:`render_spec` before the files are
    written, see :data:`PATH_RENDERED_VERSIONS` and
    :data:`CONTENT_RENDERED_VERSIONS`.

    Returns a dict with the 'version', 'files' and 'keep' of the document. Path
    order is preserved so that generated files are written in a predictable
    order.
    """
    try:
        data = yaml.load(document, Loader=StrictLoader)
    except yaml.YAMLError as e:
        raise InventorySpecError('Invalid YAML in {}: {}'.format(source, e))

    if not isinstance(data, dict):
        raise InventorySpecError(
            '{} must be a YAML dictionary, got: {}'.format(
                source, type(data).__name__))

    unknown_keys = [key for key in data if key not in SPEC_KEYS]
    if unknown_keys:
        raise InventorySpecError(
            'Unknown key(s) in {}: {}. Valid keys are: {}'.format(
                source,
                ', '.join('"{}"'.format(key) for key in sorted(unknown_keys)),
                ', '.join('"{}"'.format(key) for key in SPEC_KEYS)))

    if 'version' in data:
        version = data['version']
        if not isinstance(version, int) or isinstance(version, bool):
            raise InventorySpecError(
                'The "version" key in {} must be a number, got: {}'.format(
                    source, type(version).__name__))
        if version < 0:
            raise InventorySpecError(
                'Unknown inventory specification version {} in {}'.format(
                    version, source))
        if version > SPEC_VERSION:
            raise InventorySpecError(
                '{} requires inventory specification version {}, but this '
                'DebOps release understands version {}. Upgrade DebOps to '
                'read this document.'.format(source, version, SPEC_VERSION))
    else:
        version = DEFAULT_VERSION

    if 'files' not in data:
        raise InventorySpecError('No "files" key found in {}'.format(source))

    files = data['files']
    if not isinstance(files, dict):
        raise InventorySpecError(
            'The "files" key in {} must be a dictionary, got: {}'.format(
                source, type(files).__name__))

    for path, content in files.items():
        if not isinstance(path, str):
            raise InventorySpecError(
                'File path in {} must be a string, got: {}'.format(
                    source, type(path).__name__))
        if not path.strip():
            raise InventorySpecError('Empty file path found in {}'.format(
                source))
        if content is not None and not isinstance(content, str):
            raise InventorySpecError(
                'Contents of "{}" in {} must be a text block or null, got: '
                '{}. Use a YAML literal block to store the file contents, for '
                'example: "{}: |\\n  key: value". Use null to remove the '
                'path.'.format(
                    path, source, type(content).__name__, path))
        if path.rstrip().endswith('/') and content:
            raise InventorySpecError(
                'Directory "{}" in {} cannot have file contents. Use an empty '
                'value to clear or create the directory, or null to remove '
                'it.'.format(path, source))

    keep = data.get('keep', [])
    if not isinstance(keep, list):
        raise InventorySpecError(
            'The "keep" key in {} must be a list of paths, got: {}'.format(
                source, type(keep).__name__))

    for pattern in keep:
        if not isinstance(pattern, str):
            raise InventorySpecError(
                'Each entry of the "keep" key in {} must be a string, got: '
                '{}'.format(source, type(pattern).__name__))
        if not pattern.strip():
            raise InventorySpecError(
                'Empty path in the "keep" key of {}'.format(source))

    return {'version': version, 'files': files, 'keep': keep}


def _execute_command(command, timeout):
    """Run a shell command and capture its output.

    Kept separate from the template global so that a test can replace it
    without spawning a process.
    """
    return subprocess.run(
        command, shell=True, capture_output=True, text=True,
        encoding='utf-8', errors='replace', timeout=timeout)


def _render_globals(version, allow_io, include_base, notify):
    """Build the pipe() and include() globals for a specification document.

    The two functions are defined even for a version which is not allowed to
    use them, so that the error explains which permission is missing instead of
    reporting the name as undefined. Results are cached for the duration of one
    document, so a command or a file which is referenced from several files is
    read only once.
    """
    cache = {}

    def pipe(command, timeout=PIPE_TIMEOUT):
        if version not in IO_VERSIONS:
            raise InventorySpecError(
                'pipe() requires inventory specification version 3, this '
                'document is version {}'.format(version))

        if not allow_io:
            raise InventorySpecError(
                "pipe() is not allowed; enable it with the '--allow-io' "
                'option')

        if not isinstance(command, str) or not command.strip():
            raise InventorySpecError('pipe() needs a non-empty command string')

        key = ('pipe', command)
        if key in cache:
            return cache[key]

        if notify is not None:
            notify('Executing command: {}'.format(command))

        try:
            result = _execute_command(command, timeout)
        except subprocess.TimeoutExpired:
            raise InventorySpecError(
                'Command timed out after {} seconds: {}'.format(
                    timeout, command))

        if result.returncode != 0:
            message = result.stderr.strip()
            raise InventorySpecError(
                'Command failed with exit code {}: {}{}'.format(
                    result.returncode, command,
                    ': ' + message if message else ''))

        output = result.stdout.rstrip('\n')
        cache[key] = output
        return output

    def include(path):
        if version not in IO_VERSIONS:
            raise InventorySpecError(
                'include() requires inventory specification version 3, this '
                'document is version {}'.format(version))

        if not allow_io:
            raise InventorySpecError(
                "include() is not allowed; enable it with the '--allow-io' "
                'option')

        if not isinstance(path, str) or not path.strip():
            raise InventorySpecError('include() needs a non-empty path string')

        key = ('include', path)
        if key in cache:
            return cache[key]

        expanded = os.path.expandvars(os.path.expanduser(path))
        if not os.path.isabs(expanded):
            expanded = os.path.join(include_base, expanded)
        expanded = os.path.abspath(expanded)

        if notify is not None:
            notify('Including file: {}'.format(expanded))

        try:
            with open(expanded, 'r', encoding='utf-8') as fh:
                contents = fh.read()
        except IsADirectoryError:
            raise InventorySpecError(
                'Cannot include "{}": it is a directory'.format(path))
        except UnicodeDecodeError:
            raise InventorySpecError(
                'Cannot include "{}": it is not a UTF-8 text file'.format(
                    path))
        except OSError as e:
            raise InventorySpecError(
                'Cannot include "{}": {}'.format(path, e))

        cache[key] = contents
        return contents

    return {'pipe': pipe, 'include': include}


def _render_string(environment, context, template, source, what, hint=''):
    """Render one Jinja2 template string, reporting failures with its context.

    Shared by path names and file contents so that both failure modes read the
    same way. var:`what` names the thing being rendered, var:`hint` is appended
    to an undefined-variable error for extra guidance.
    """
    try:
        return environment.from_string(template).render(**context)
    except jinja2.TemplateSyntaxError as e:
        raise InventorySpecError(
            'Cannot render {} in {}: {}'.format(what, source, e))
    except jinja2.UndefinedError as e:
        raise InventorySpecError(
            'Cannot render {} in {}: {}{}'.format(what, source, e, hint))
    except InventorySpecError as e:
        raise InventorySpecError(
            'Cannot render {} in {}: {}'.format(what, source, e))


def render_spec(files, context, source='inventory specification', version=2,
                allow_io=False, include_base=None, notify=None,
                render_paths=True, render_contents=True):
    """Render file paths and contents of a specification as Jinja2 templates.

    A version listed in :data:`PATH_RENDERED_VERSIONS` has its path keys
    rendered, so that a path such as ``host_vars/{{ hostname }}/main.yml``
    follows the same host name as the files which refer to it. A version listed
    in :data:`CONTENT_RENDERED_VERSIONS` has its file contents rendered as
    well; the contents of the other versions are passed through untouched. A
    version which asks for neither is never run through this function.

    Undefined variables are an error rather than an empty string, so a mistyped
    variable is reported instead of quietly blanking out a value. Two different
    keys which render to the same path within one document are rejected; a
    document with an empty rendered path is rejected as well.

    'trim_blocks' is deliberately left off and 'keep_trailing_newline' is
    turned on. The DebOps project templates enable 'trim_blocks' because a
    block tag at the end of a line is meant to be followed by a line break;
    here the contents belong to the user, where removing that newline would
    silently join two lines of an inventory or a variables file. Jinja also
    drops the final newline of a template by default, which would make a
    rendered file differ from a literal one by a single newline. Whitespace
    control stays available through Jinja's '-' modifiers.

    A document whose version is listed in :data:`IO_VERSIONS` may use the
    pipe() and include() globals, and only when var:`allow_io` is true; a
    relative path given to include() is resolved against var:`include_base`.
    var:`notify` is an optional callable used to report each command and file.

    Returns a dict of inventory-relative path to rendered contents.
    """
    include_base = os.path.abspath(include_base or os.getcwd())
    environment = jinja2.Environment(
        undefined=jinja2.StrictUndefined, keep_trailing_newline=True)
    environment.globals.update(
        _render_globals(version, allow_io, include_base, notify))

    rendered = {}

    for path, content in files.items():
        rendered_path = path

        if render_paths:
            rendered_path = _render_string(
                environment, context, path, source,
                'path "{}"'.format(path))

            if not rendered_path.strip():
                raise InventorySpecError(
                    'Path "{}" in {} rendered to an empty string'.format(
                        path, source))

            if rendered_path in rendered:
                raise InventorySpecError(
                    'Multiple paths in {} render to the same file: "{}"'.format(
                        source, rendered_path))

        if content is None or not render_contents:
            rendered[rendered_path] = content
            continue

        rendered[rendered_path] = _render_string(
            environment, context, content, source,
            'contents of "{}"'.format(path), hint=(
                '. If this is an Ansible expression which should reach the '
                'file unchanged, escape it with \'{{ "{{" }}\' and '
                '\'{{ "}}" }}\', or wrap it in a \'{{% raw %}}\' block.'))

    return rendered


def render_keep(keep, context, source='inventory specification', version=2):
    """Render the 'keep' patterns of a specification as Jinja2 templates.

    Kept patterns are paths like the ones in 'files', so a document which
    renders its paths renders these too: a version listed in
    :data:`PATH_RENDERED_VERSIONS` may write ``keep: ['{{ view }}/custom.yml']``.
    The patterns are not passed through :func:`_render_globals`, since keeping
    a path is not an operation which reads or runs anything.

    Returns a list of rendered patterns.
    """
    if version not in PATH_RENDERED_VERSIONS:
        return list(keep)

    environment = jinja2.Environment(
        undefined=jinja2.StrictUndefined, keep_trailing_newline=True)

    return [_render_string(environment, context, pattern, source,
                           'kept path "{}"'.format(pattern))
            for pattern in keep]


def load_template(name):
    """Load an inventory specification shipped with the DebOps package.

    Raises InventorySpecError for an unknown name, or for a name which tries
    to reach outside of the template directory.
    """
    # The name comes from the command line and is turned into a path inside
    # the package data, so anything which is not a bare file name is refused
    # instead of being normalized into a traversal.
    available = ', '.join('"{}"'.format(item) for item in SPEC_TEMPLATES)

    if not name or '/' in name or '\\' in name or os.sep in name or \
            name in ('.', '..'):
        raise InventorySpecError(
            'Invalid inventory specification template name: "{}". Expected '
            'one of: {}'.format(name, available))

    if name not in SPEC_TEMPLATES:
        raise InventorySpecError(
            'Unknown inventory specification template "{}". Available '
            'templates: {}'.format(name, available))

    document = pkgutil.get_data('debops',
                                os.path.join(TEMPLATE_DIR, name + '.yml'))

    if document is None:
        raise InventorySpecError(
            'Inventory specification template "{}" is missing from the DebOps '
            'installation, expected at {}'.format(
                name, os.path.join(TEMPLATE_DIR, name + '.yml')))

    return parse_spec(document.decode('utf-8'),
                      'template "{}"'.format(name))


def _keep_matcher(patterns):
    """Build a predicate which reports whether an inventory-relative path is
    protected by a 'keep' pattern list.

    A path is kept when a pattern matches it, or when a pattern matches one of
    its parent directories, so that keeping a directory protects everything
    inside it without the document having to name each one. Patterns are
    matched with :func:`fnmatch.fnmatchcase`, which is case-sensitive on every
    platform, and whose ``*`` also matches the path separator: ``*`` and ``**``
    are therefore equivalent, and a pattern like ``group_vars/*.yml`` reaches
    ``group_vars/all/keyring.yml``.

    A pattern which matches more than it was meant to keeps too many paths
    rather than too few, which is the safer direction for an operation whose
    job is to delete things.
    """
    normalized = [pattern.rstrip('/') for pattern in patterns]

    def matches(path):
        candidate = path.rstrip('/')

        for pattern in normalized:
            probe = candidate
            while True:
                if fnmatch.fnmatchcase(probe, pattern):
                    return True

                parent = os.path.dirname(probe)
                if not parent or parent == probe:
                    break
                probe = parent

        return False

    return matches


def resolve_keep(patterns, base_dir):
    """Validate the 'keep' path patterns of a specification.

    A pattern is validated like a path in 'files': it is relative to the
    inventory directory, must not contain '~', and must not escape that
    directory through '..' components. Wildcards are allowed, so a pattern is
    never looked up on disk and does not have to exist.

    Returns a predicate which takes an absolute path and reports whether the
    'keep' patterns protect it.
    """
    validated = []

    for pattern in patterns:
        expanded = os.path.expandvars(pattern)

        if os.path.isabs(expanded) or os.path.expanduser(pattern) != pattern:
            raise InventorySpecError(
                'Kept path "{}" must be relative to the Ansible inventory '
                'directory and must not contain "~"'.format(pattern))

        parts = [part for part in expanded.replace(os.sep, '/').split('/')
                 if part and part != '.']

        if not parts:
            raise InventorySpecError(
                'Kept path "{}" in the inventory specification does not name '
                'a path'.format(pattern))

        if os.pardir in parts:
            raise InventorySpecError(
                'Kept path "{}" must not contain "{}" components'.format(
                    pattern, os.pardir))

        validated.append('/'.join(parts))

    matcher = _keep_matcher(validated)
    base_dir = os.path.realpath(base_dir)

    def keeps(path):
        try:
            relative = os.path.relpath(os.path.realpath(path), base_dir)
        except ValueError:
            # A path on another filesystem has no relative form here
            return False

        if relative.startswith(os.pardir):
            return False

        return matcher(relative.replace(os.sep, '/'))

    return keeps


def merge_specs(specs):
    """Merge multiple parsed specifications into a single file mapping.

    Accepts a list of (source, spec) pairs, where spec is what :func:`parse_spec`
    returns. Paths defined in later specifications replace earlier ones; the
    override is reported through the returned list of notices rather than
    silently.

    The 'keep' lists are unioned rather than replaced, so that a specification
    cannot drop the protection another one asked for. A document which writes a
    path that another one keeps is rejected: the two instructions contradict
    each other, and picking one of them silently would hide the mistake.

    Returns a dict of merged files, a list of kept path patterns and a list of
    notices.
    """
    merged = {}
    keep = []
    notices = []

    for source, spec in specs:
        for path, content in spec['files'].items():
            if path in merged:
                notices.append(
                    'File "{}" from {} replaces an earlier definition'.format(
                        path, source))
            merged[path] = content

        for pattern in spec['keep']:
            if pattern not in keep:
                keep.append(pattern)

    # Matched against the merged paths, so that a glob in one document protects
    # a file which another document writes. Environment variables are expanded
    # on both sides here, the way resolve_paths() and resolve_keep() expand them
    # later, so that two spellings of the same path are still recognized as one
    matcher = _keep_matcher([os.path.expandvars(pattern) for pattern in keep])
    for source, spec in specs:
        for path in spec['files']:
            if matcher(os.path.expandvars(path)):
                raise InventorySpecError(
                    'Path "{}" from {} is also listed in the "keep" key, so '
                    'the specification contradicts itself about it'.format(
                        path, source))

    return merged, keep, notices


def resolve_paths(files, base_dir):
    """Expand environment variables in paths, then map them under base_dir.

    Paths are relative to base_dir and must stay inside it. Absolute paths and
    paths which escape base_dir through '..' components or symbolic links are
    rejected, since a specification is an untrusted write primitive. A path
    which ends in a separator marks a directory rather than a file.

    Returns a dict which maps the real path of each entry to a
    :data:`ResolvedEntry`. The real path is used as the key so that two entries
    which reach the same file through different environment variables are still
    rejected.
    """
    base_dir = os.path.realpath(base_dir)
    resolved = {}

    for path, content in files.items():
        expanded = os.path.expandvars(path)

        if os.path.isabs(expanded) or os.path.expanduser(path) != path:
            raise InventorySpecError(
                'File path "{}" must be relative to the Ansible inventory '
                'directory and must not contain "~"'.format(path))

        is_dir = expanded.rstrip().endswith('/')
        if is_dir and content:
            raise InventorySpecError(
                'Directory "{}" cannot have file contents. Use an empty value '
                'to clear or create it, or null to remove it.'.format(path))

        target_path = os.path.abspath(
            os.path.join(base_dir, expanded.rstrip().rstrip('/')))
        target = os.path.realpath(target_path)

        # A specification must not be able to write outside of the inventory
        # directory it was given, not even through a symbolic link.
        if target != base_dir and not target.startswith(base_dir + os.sep):
            raise InventorySpecError(
                'File path "{}" points outside of the Ansible inventory '
                'directory'.format(path))

        if target == base_dir:
            raise InventorySpecError(
                'File path "{}" refers to the Ansible inventory directory '
                'itself'.format(path))

        # Two entries can resolve to the same path once environment variables
        # are expanded, for example when the same directory is reachable
        # through two different variable names.
        if target in resolved:
            raise InventorySpecError(
                'Multiple file paths in the specification resolve to the same '
                'file: "{}"'.format(path))

        resolved[target] = ResolvedEntry(path=target_path, content=content,
                                         is_dir=is_dir)

    return resolved


def _assert_no_symlinks(entry, base_dir):
    """Refuse to touch a path which is, or goes through, a symbolic link.

    A symbolic link can point anywhere, including outside of the inventory, so
    a specification is not allowed to write through one or to remove one, not
    even with '--force'. Every component of the path is checked, as well as
    everything inside a directory which is about to be cleared.
    """
    if os.path.islink(entry.path):
        raise InventorySpecError(
            'Refusing to modify "{}": it is a symbolic link'.format(
                os.path.relpath(entry.path, base_dir)))

    current = base_dir
    for part in os.path.relpath(entry.path, base_dir).split(os.sep):
        current = os.path.join(current, part)
        if os.path.islink(current):
            raise InventorySpecError(
                'Refusing to modify "{}": "{}" is a symbolic link'.format(
                    os.path.relpath(entry.path, base_dir),
                    os.path.relpath(current, base_dir)))

    if entry.is_dir and os.path.isdir(entry.path):
        for root, dirs, files in os.walk(entry.path, followlinks=False):
            for name in list(dirs) + list(files):
                child = os.path.join(root, name)
                if os.path.islink(child):
                    raise InventorySpecError(
                        'Refusing to modify "{}": it contains the symbolic '
                        'link "{}"'.format(
                            os.path.relpath(entry.path, base_dir),
                            os.path.relpath(child, base_dir)))


def _is_protected(target, pre_existing, is_dir):
    """Report whether a path was already present before this command started.

    A directory is protected when it existed itself, or when it contains a
    pre-existing path, so that removing the directory cannot silently drop a
    file the user wrote.
    """
    if target in pre_existing:
        return True
    if is_dir:
        prefix = target + os.sep
        if any(path.startswith(prefix) for path in pre_existing):
            return True
    return False


def _clear_directory(path, keeps, dry_run, result):
    """Delete everything under a directory except the paths which are kept.

    Returns True when something survived, so that the caller can tell whether
    the directory itself can go. The tree is walked bottom-up and a directory
    is only removed when nothing kept is left inside it, which is what preserves
    the directories above a kept file without the document naming them.

    Symbolic links are not handled here: a directory which contains one is
    refused before any of this runs.
    """
    survivors = set()

    for root, dirs, files in os.walk(path, topdown=False, followlinks=False):
        for name in files:
            child = os.path.join(root, name)

            if keeps(child):
                result['kept'].append(child)
                survivors.add(root)
                continue

            if dry_run:
                result['planned_removed'].append(child)
            else:
                os.remove(child)
                result['removed'].append(child)

        for name in dirs:
            child = os.path.join(root, name)

            if keeps(child):
                result['kept'].append(child)
                survivors.add(child)

            if child in survivors:
                # Content which survived keeps every directory above it alive,
                # up to the directory being cleared
                survivors.add(root)
            elif dry_run:
                result['planned_removed'].append(child)
            else:
                os.rmdir(child)
                result['removed'].append(child)

    return path in survivors


def _remove_entry(target, entry, keeps, pre_existing, overwrite, dry_run,
                  result):
    if not os.path.exists(entry.path):
        return

    # A kept path is left alone before the overwrite check, because '--force'
    # must not be able to remove what the specification asked to keep
    if keeps(target):
        result['kept'].append(target)
        return

    # Whether the path is a directory is decided by the filesystem, not by the
    # trailing separator in the specification, so that a removal written
    # without the separator still clears a directory instead of failing
    is_dir = os.path.isdir(entry.path)

    if not overwrite and _is_protected(target, pre_existing, is_dir):
        result['skipped'].append(target)
        return

    if is_dir:
        survived = _clear_directory(entry.path, keeps, dry_run, result)
        if survived:
            # The directory was not named by a 'keep' pattern itself, but it
            # holds content which was, and the documented meaning of 'keep'
            # covers the directories above the paths it names
            result['kept'].append(target)
            return

        if dry_run:
            result['planned_removed'].append(target)
            return

        os.rmdir(entry.path)
    elif dry_run:
        result['planned_removed'].append(target)
        return
    else:
        os.remove(entry.path)

    result['removed'].append(target)


def _empty_dir(target, entry, keeps, pre_existing, overwrite, dry_run, result):
    # A kept path is reported as kept rather than as skipped, so that the user
    # can tell a path which was spared by 'keep' from one which was spared by a
    # missing '--force'
    if keeps(target):
        result['kept'].append(target)
        return

    if not overwrite and _is_protected(target, pre_existing, True):
        result['skipped'].append(target)
        return

    if os.path.isdir(entry.path):
        _clear_directory(entry.path, keeps, dry_run, result)
    elif os.path.exists(entry.path):
        if dry_run:
            result['planned_removed'].append(target)
        else:
            os.remove(entry.path)
            result['removed'].append(target)

    if not dry_run:
        os.makedirs(entry.path, exist_ok=True)

    result['planned' if dry_run else 'written'].append(target)


def apply_spec(files, base_dir, pre_existing=frozenset(), overwrite=False,
               dry_run=False, keep=()):
    """Apply the paths described by a specification under base_dir.

    A value which is a string writes a file. A value of None removes the path;
    a directory removal is recursive, and a path which is a directory on disk is
    removed as one whether or not the document spelled a separator after it. A
    path which ends in a separator with an empty value is an empty directory:
    an existing directory is cleared in place, a missing one is created.
    Removals are performed before writes, so that a directory can be removed and
    re-created by another entry in the same specification.

    The 'keep' patterns name paths which the specification must not remove or
    clear, together with the directories above them. They are honored even with
    overwrite set, and a kept path is reported instead of being changed. See
    :func:`resolve_keep`.

    Paths which already exist are not modified unless overwrite is True; they
    are reported as skipped instead. pre_existing is the set of absolute paths
    which were present before the specification was applied, which lets a
    specification replace the files that DebOps itself just generated while
    still protecting files the user has edited. Symbolic links are refused
    regardless of overwrite.

    Returns a dict with 'written', 'removed', 'skipped', 'kept', 'planned' and
    'planned_removed' lists of absolute paths, sorted by path.
    """
    result = {'written': [], 'removed': [], 'skipped': [], 'kept': [],
              'planned': [], 'planned_removed': []}
    pre_existing = set(pre_existing)
    base_dir = os.path.realpath(base_dir)

    resolved = resolve_paths(files, base_dir)
    keeps = resolve_keep(keep, base_dir)

    # Symlinks are refused before anything is changed, so that a refusal leaves
    # the inventory untouched.
    for entry in resolved.values():
        _assert_no_symlinks(entry, base_dir)

    ordered = sorted(resolved.items())

    for target, entry in ordered:
        if entry.content is None:
            _remove_entry(target, entry, keeps, pre_existing, overwrite,
                          dry_run, result)

    for target, entry in ordered:
        if entry.is_dir and entry.content == '':
            _empty_dir(target, entry, keeps, pre_existing, overwrite, dry_run,
                       result)

    for target, entry in ordered:
        if entry.content is None or entry.is_dir:
            continue

        # merge_specs() refuses a specification which writes a path that it
        # also keeps, so this only triggers for a caller which assembles the
        # mapping itself; keeping the path is the answer which matches the
        # documented rule, and it is the one which loses no data
        if keeps(target):
            result['kept'].append(target)
            continue

        if not overwrite and target in pre_existing:
            result['skipped'].append(target)
            continue

        if dry_run:
            result['planned'].append(target)
            continue

        if os.path.isdir(entry.path):
            raise InventorySpecError(
                'Cannot write "{}": it is a directory'.format(
                    os.path.relpath(entry.path, base_dir)))

        if write_file(entry.path, entry.content, overwrite=True):
            result['written'].append(target)

    for paths in result.values():
        paths.sort()

    result['kept'] = sorted(set(result['kept']))

    return result
