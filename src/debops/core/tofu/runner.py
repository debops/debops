# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu runner of the project views.

The :class:`TofuRunner` executes :command:`tofu` operations in the
context of a DebOps project directory: with the project's environment,
the view's hook scripts around the operation and the view's secret
store unlocked for the duration. The tool-agnostic machinery lives in
:class:`debops.core.runner.Runner`; this module adds the tofu argument
parsing, the runner-owned environment of the tofu subprocess, the
state lock pre-check and the missing-state refusal.
"""

from ..runner import Runner
from ..hooks import run_hooks
from . import cache
from .binary import resolve_binary
from .providers import resolve_providers
from .modules import resolve_modules
from .registry import view_drop_in_path, view_tofu_root
from .view import create_view
import datetime
import dotenv
import fcntl
import json
import logging
import os
import re
import shlex
import subprocess
import sys

logger = logging.getLogger(__name__)

# Flags of the tofu command line which take no value of their own.
# Every other leading-dash token carries a value: either in the same
# token ('-input=false', '-var=name=value') or in the token which
# follows it.
TOFU_FLAGS = [
    '-auto-approve', '-compact-warnings', '-concise',
    '-consolidate-errors', '-destroy', '-detailed-exitcode', '-dry-run',
    '-force-copy', '-h', '--help', '-json', '-migrate-state',
    '-no-color', '-reconfigure', '-refresh-only', '-upgrade'
]

# The operations which accept the '-input=false' option. The runner
# adds it to the operations which could prompt for input, so that an
# open stdin fails fast instead of blocking on a prompt; the other
# operations do not accept the option at all.
INPUT_OPERATIONS = frozenset([
    'apply', 'console', 'destroy', 'import', 'init', 'plan', 'refresh'
])

# The operations which touch the state of the view: the runner checks
# the presence of the state before them, because a missing state makes
# OpenTofu silently re-initialize with a fresh lineage and plan to
# create all infrastructure again. 'init' is exempt -- it is the way
# out of the refusal -- and so are the operations which never read or
# write state files.
STATE_OPERATIONS = frozenset([
    'apply', 'console', 'destroy', 'import', 'output', 'plan', 'refresh',
    'show', 'state', 'taint', 'test', 'untaint'
])

# The operations which acquire the state lock for their duration: the
# runner pre-checks the lock before them, so that a concurrent run
# fails before a subprocess is spawned.
LOCK_OPERATIONS = frozenset([
    'apply', 'destroy', 'import', 'plan', 'refresh', 'state', 'taint',
    'untaint'
])

# The operations which change infrastructure without applying a saved
# plan file: the wrapper asks for their approval, because with
# '-input=false' OpenTofu does not ask itself.
DESTRUCTIVE_OPERATIONS = frozenset(['apply', 'destroy'])

# The usage lines of the OpenTofu help screens name the raw binary;
# the wrapper rewrites them so that the help does not teach the
# invocations which bypass it
USAGE_LINE = re.compile(r'^Usage: tofu(?=[\s$])', re.MULTILINE)

# The plan files DebOps saves live in the view's encrypted store, so
# that the plan file is encrypted at rest. The 'debops-' prefix marks
# the files the plan retention prunes: the plan files the operator
# saves with the '-out' option are never touched.
PLAN_DIR = os.path.join('secret', 'plans')
PLAN_FILE_PREFIX = 'debops-'


class TofuRunner(Runner):

    def __init__(self, project, tofu_args, bell=False, no_color=False,
                 workspace=None, providers=None, modules=None):
        super().__init__(project, bell=bell, secrets_name='tofu')

        self._providers = providers
        self._modules = modules
        self._view_root = self._view_tofu_root()
        for flag, set_name in (('--provider', 'provider set'),
                               ('--module', 'module set')):
            options = providers if flag == '--provider' else modules
            if not options or not self._view_exists():
                continue
            # The '--provider' and '--module' options apply when a view
            # is created: the dependency set of an existing view is
            # recorded in its configuration drop-in, which the user owns
            if os.path.exists(view_drop_in_path(project, project.view)):
                raise ValueError(
                    "The '{}' options apply when a view is created: the "
                    '{} of the view {!r} is already recorded in its '
                    'configuration drop-in. Edit the drop-in and run '
                    "'debops tofu update' to reconcile the generated "
                    'files.'.format(flag, set_name, project.view))
            raise ValueError(
                "The '{}' options apply when a view is created: the "
                'view {!r} already exists and manages its own '
                'requirements.'.format(flag, project.view))
        self._operation = tofu_args[0]
        if not re.fullmatch(r'[a-z]+(-[a-z]+)*', self._operation):
            raise ValueError(
                "The token '{}' is not an OpenTofu operation.".format(
                    self._operation))
        self._workspace = self._resolve_workspace(workspace)
        self._state_path = self._resolve_state_path()
        self._data_dir = cache.data_dir(project)
        self._plugin_cache = cache.plugin_cache()

        self._tofu_env = {
            'TF_DATA_DIR': self._data_dir,
            'TF_PLUGIN_CACHE_DIR': self._plugin_cache,
            'TF_WORKSPACE': self._workspace,
        }
        # Creating or selecting a workspace requires the environment
        # variable to carry the name of the workspace the command
        # targets: OpenTofu refuses the mismatch
        if (self._operation == 'workspace' and len(tofu_args) > 2
                and tofu_args[1] in ('new', 'select')):
            self._tofu_env['TF_WORKSPACE'] = tofu_args[2]
        cli_config = os.path.join(project.path, '.debops', 'tofu',
                                  'cli.tfrc')
        if os.path.isfile(cli_config):
            self._tofu_env['TF_CLI_CONFIG_FILE'] = cli_config

        self._plan_saved = False
        self._plan_file = None
        self._informational = (
            self._operation == 'help'
            or any(argument in ('-h', '--help') for argument in tofu_args))
        self._tofu_command = self._build_command(tofu_args,
                                                 no_color=no_color)

    def _view_exists(self):
        """Whether the view already has its tree or its configuration
        drop-in."""
        return (os.path.exists(os.path.join(self._view_root, 'main.tf'))
                or os.path.exists(view_drop_in_path(self.project,
                                                    self.project.view)))

    def _view_tofu_root(self):
        """Return the view's tofu directory the operation runs in."""
        return view_tofu_root(self.project, self.project.view)

    def _resolve_workspace(self, workspace):
        """Return the workspace the operations run against.

        The command line overrides the view's configured workspace,
        which itself defaults to the 'default' workspace of the local
        backend: one state directory per view.
        """
        if workspace:
            return workspace
        try:
            return self.project.config.raw['views'][self.project.view][
                'tofu']['workspace']
        except (KeyError, TypeError):
            return 'default'

    def _resolve_state_path(self):
        """Return the local state path of the view.

        The path is relative to the view's tofu directory, where the
        backend block of the view configuration points as well. An
        empty value marks a view with a remote backend: the local
        state checks are skipped.
        """
        try:
            state_path = self.project.config.raw['views'][
                self.project.view]['tofu']['state_path']
        except (KeyError, TypeError):
            try:
                state_path = self.project.config.raw['tofu']['state_path']
            except (KeyError, TypeError):
                state_path = 'secret/terraform.tfstate'
        return state_path

    def _resolve_binary(self):
        """Return the binary which the operation runs with.

        The view's configuration drop-in records the pinned version
        when it exists: the managed binary of that version runs when
        it is installed, the configured binary falls back otherwise.
        The resolution happens after the view exists -- a freshly
        created view carries its seeded version, which 'debops tofu
        install' installs.
        """
        return resolve_binary(self.project, self.project.view)

    def _build_command(self, tofu_args, no_color=False):
        """Build the tofu command line, preserving argument order.

        The runner's own options come last, where a repeated flag
        overrides the ones the operator passed: '-input=false' is the
        non-interactive contract of the wrapper on the operations
        which accept it, and '-no-color' is added when the output
        streams are consumed by a program rather than shown on a
        terminal -- OpenTofu emits ANSI color codes even when the
        output is not a terminal. The command carries the configured
        binary as its placeholder; the resolution replaces it after
        the view exists.

        A 'plan' without the '-out' option is saved into the view's
        encrypted store: the plan file carries the planned state of
        the view, which is encrypted at rest with the state, and the
        plan retention prunes the expired ones.
        """
        command = [
            self.project.config.raw['binaries']['tofu']
        ]
        parsed_args = self._parse_tofu_args(tofu_args)
        command.extend(parsed_args)
        if self._operation == 'plan' and self._plan_retention() > 0:
            if not any(arg == '-out' or arg.startswith('-out=')
                       for arg in command):
                self._plan_file = self._plan_file_path()
                command.append('-out={}'.format(self._plan_file))
                self._plan_saved = True
        if self._operation not in ('state', 'workspace') and no_color:
            command.append('-no-color')
        if self._operation in INPUT_OPERATIONS:
            command.append('-input=false')
        return command

    def _parse_tofu_args(self, tofu_args):
        """Parse the arguments meant for tofu, preserving their order.

        A leading-dash token which carries a value inside itself
        ('-input=false', '-var=name=value') is self-contained; the
        flags without a value of their own are named in
        :var:`TOFU_FLAGS`; every other leading-dash token consumes the
        token which follows it as its value. Positional arguments --
        the operation name and, for 'apply', the plan file -- pass
        through unchanged; their indexes in the original arguments
        are recorded in :attr:`_positional_indexes`.
        """
        parsed_args = []
        consumed = set()
        self._positional_indexes = []
        arg_length = len(tofu_args)
        for index, argument in enumerate(tofu_args):
            if argument == '--':
                continue
            if index in consumed:
                continue
            if (argument.startswith('-') and argument != '-'):
                if '=' in argument or argument in TOFU_FLAGS:
                    parsed_args.append(argument)
                    continue
                if (index + 1 < arg_length
                        and not tofu_args[index + 1].startswith('-')):
                    parsed_args.extend([argument, tofu_args[index + 1]])
                    consumed.update([index, index + 1])
                    continue
            parsed_args.append(argument)
            self._positional_indexes.append(index)
        return parsed_args

    def _secret_dir(self):
        """Return the view's secret directory, the store's mount point."""
        return os.path.join(self._view_root, 'secret')

    def _plan_retention(self):
        """How many plan files the DebOps flows keep in the view's
        store."""
        try:
            return self.project.config.raw['tofu']['plan_retention']
        except (KeyError, TypeError):
            return 3

    def _plan_file_path(self):
        """Return the path of the plan file DebOps saves.

        The file lives in the view's encrypted store: the plan file
        carries the planned state of the view, which is encrypted at
        rest with the state. The timestamped name sorts
        lexicographically by age, and the 'debops-' prefix marks the
        files the retention prunes -- the plan files the operator
        saves with the '-out' option are never touched.
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        return os.path.join(PLAN_DIR,
                            '{}{}.tfplan'.format(PLAN_FILE_PREFIX, timestamp))

    def _announce_saved_plan(self):
        """Announce the plan file the operation saved."""
        logger.notice(
            "Saved the plan file '{}' of the view {!r}".format(
                self._plan_file, self.project.view),
            extra={'allow': ['stderr', 'syslog']})

    def _prune_plans(self):
        """Prune the expired plan files DebOps saved in the view's
        store.

        The plan files DebOps saves carry the 'debops-' prefix; the
        retention keeps the newest 'plan_retention' of them and
        removes the older ones. The plan files the operator saves
        with the '-out' option are never touched.
        """
        plans_dir = os.path.join(self._view_root, PLAN_DIR)
        saved = sorted(
            name for name in os.listdir(plans_dir)
            if name.startswith(PLAN_FILE_PREFIX) and name.endswith('.tfplan'))
        for name in saved[:-self._plan_retention()]:
            os.remove(os.path.join(plans_dir, name))
            logger.notice(
                "Removed the expired plan file '{}' of the view "
                '{!r}'.format(os.path.join(PLAN_DIR, name),
                              self.project.view),
                extra={'allow': ['stderr', 'syslog']})

    def _extra_env(self):
        """Return the runner's own additions to the subprocess
        environment.

        The environment file inside the unlocked store carries the
        state passphrase and the provider credentials of the view;
        their values compose into the subprocess environment last, so
        that a rotated value in the store wins over a stale one
        exported in the operator's session. The variables reach the
        tofu subprocess only, never the hook scripts.
        """
        env = dict(self._tofu_env)
        store_env = os.path.join(self._secret_dir(), '.env')
        if os.path.isfile(store_env):
            env.update({key: value
                        for key, value in dotenv.dotenv_values(
                            store_env).items()
                        if value is not None})
        return env

    def _state_file(self):
        """Return the state file the operation reads and writes.

        The paths come from the backend configuration OpenTofu
        recorded at initialization, so that the checks look where the
        view's own configuration points: the default workspace keeps
        its state at the backend's path, the named workspaces in the
        backend's workspace directory, and without an initialization
        the layout of the shipped view template applies.
        """
        backend = self._backend_metadata()
        if self._workspace == 'default':
            state_path = self._state_path
            if backend and backend.get('path'):
                state_path = backend['path']
            return os.path.join(self._view_root, state_path)

        if backend:
            if backend.get('workspace_dir'):
                return os.path.join(self._view_root,
                                    backend['workspace_dir'],
                                    self._workspace, 'terraform.tfstate')
            return os.path.join(self._view_root, 'terraform.tfstate.d',
                                self._workspace, 'terraform.tfstate')
        return os.path.join(self._view_root,
                            os.path.dirname(self._state_path),
                            'workspaces', self._workspace,
                            'terraform.tfstate')

    def _backend_metadata(self):
        """Return the effective local backend configuration of the
        view, as OpenTofu recorded it at initialization.

        The relocated data directory holds the metadata of the
        initialization; its backend section carries the state path and
        the workspace directory the view's configuration is effective
        with. Views with a remote backend and views which were never
        initialized on this machine have none.
        """
        try:
            with open(os.path.join(self._data_dir,
                                   'terraform.tfstate')) as handle:
                backend = json.load(handle)['backend']
        except (OSError, ValueError, KeyError, TypeError):
            return None
        if backend.get('type') != 'local':
            return None
        config = backend.get('config')
        return config if isinstance(config, dict) else {}

    def _state_checks_enabled(self):
        """Whether the local state checks apply to the view.

        A view with a remote backend has no local state file to
        check; the configuration says so with an empty state path.
        """
        return bool(self._state_path)

    def _initialized_before(self):
        """Whether the view was initialized on this machine before.

        The relocated data directory holds the backend metadata of
        the initialization; its presence separates a view whose state
        is missing from a view which never had one.
        """
        return os.path.exists(os.path.join(self._data_dir,
                                           'terraform.tfstate'))

    def _check_state_presence(self):
        """Refuse the operation when the state the view should have is
        not there.

        With the state file missing, tofu silently re-initializes
        with a fresh lineage and plans to create all infrastructure
        again. A view which was initialized on this machine before
        must hold a state file in its unlocked store; the missing
        state means the store is locked, empty or mounted empty. A
        named workspace which does not exist is refused as well: tofu
        would silently create it on selection and plan against empty
        state. Both are the one hard refusal of the wrapper; a view
        without a state file yet passes, its first operation is the
        legitimate creation.
        """
        if not self._state_checks_enabled():
            return

        state_file = self._state_file()
        if os.path.exists(state_file):
            return

        if self._workspace != 'default':
            if not self._initialized_before():
                raise ChildProcessError(
                    'The view is not initialized; run '
                    "'debops tofu init' before the operations which "
                    'touch its state.')
            if not os.path.isdir(os.path.dirname(state_file)):
                raise ChildProcessError(
                    "The workspace '{}' of the view does not exist. "
                    'OpenTofu would silently create it and plan against '
                    'empty state; create it explicitly with '
                    "'debops tofu workspace new {}'.".format(
                        self._workspace, self._workspace))
            # The workspace directory exists: an absent state file is
            # a fresh workspace, its first operation is the
            # legitimate creation
            return

        if self._initialized_before():
            # The state file is missing on an initialized view: a
            # fresh view holds none until its first operation, but a
            # lost store looks the same. OpenTofu would silently
            # re-initialize the state and plan to create all
            # infrastructure -- the operator sees the plan, and the
            # approval gate of the destructive operations shows it
            # before the change runs
            logger.warning(
                'The state file of the view ({}) is missing while the '
                'view was initialized on this machine before. If the '
                'state was lost, OpenTofu will plan to create all of '
                'the infrastructure again; the operations which '
                'change state show the plan before '
                'applying it.'.format(state_file),
                extra={'allow': ['stderr', 'syslog']})

    def _check_state_lock(self):
        """Refuse the operation while another process holds the state.

        OpenTofu excludes concurrent runs with a POSIX record lock on
        the state file itself; the metadata file it writes afterwards
        proves nothing about the liveness of a lock. The pre-check
        attempts the same record lock and releases it again -- tofu
        re-acquires the lock for the duration of the operation, and a
        window between the release and the re-acquisition is benign.
        """
        if not self._state_checks_enabled():
            return

        state_file = self._state_file()
        if not os.path.exists(state_file):
            return

        try:
            handle = os.open(state_file, os.O_RDWR)
        except OSError as error:
            raise ChildProcessError(
                'Cannot open the state file of the view for the lock '
                'pre-check: ' + str(error))

        try:
            fcntl.lockf(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ChildProcessError(
                'The state of the view is locked by another process; '
                'wait for the running operation to finish.')
        finally:
            os.close(handle)

    def _operation_allowed(self):
        """Whether the wrapper is configured to run the operation.

        The 'operations' list of the tofu section names the operations
        the wrapper runs; an empty list runs every one of them. The
        raw tofu command is not affected by the option.
        """
        try:
            operations = self.project.config.raw['tofu']['operations']
        except (KeyError, TypeError):
            return True
        if not operations:
            return True
        return self._operation in operations

    def _plan_file_given(self):
        """Whether the 'apply' operation applies a saved plan file.

        A plan file is pre-approved by construction: the operation
        which produced it carried the review, and OpenTofu applies it
        without asking again.
        """
        if self._operation != 'apply':
            return False
        return any(index > 0 for index in self._positional_indexes)

    def _check_approval(self):
        """Refuse a destructive one-step operation without approval.

        With '-input=false' OpenTofu does not ask for the approval of
        a one-step 'apply' or 'destroy' -- it fails the operation
        with an end-of-input error. The wrapper asks instead: an
        explicit '-auto-approve' on the command line is the decision,
        on a terminal the wrapper confirms the operation, and without
        a terminal the operation is refused with the way out.
        """
        if self._operation not in DESTRUCTIVE_OPERATIONS:
            return
        if '-auto-approve' in self._tofu_command:
            return
        if self._plan_file_given():
            return

        if sys.stdin.isatty():
            answer = input(
                "Run 'tofu {}' against the view '{}'? Only 'yes' "
                'approves: '.format(self._operation, self.project.view))
            if answer.strip().lower() in ('y', 'yes'):
                self._tofu_command.append('-auto-approve')
                return
            raise SystemExit('... aborted by user')

        raise ChildProcessError(
            "The one-step 'tofu {}' needs an approval which the "
            'non-interactive operation cannot ask for. Pass '
            "'-auto-approve' to accept the operation explicitly, or "
            'save a plan first and apply the plan file.'.format(
                self._operation))

    def _run_informational(self):
        """Run an informational operation -- the help surfaces of
        OpenTofu.

        The machinery of the wrapper does not apply to them: the store
        does not cycle, the operations allow-list and the hooks do not
        gate them, and the view tree is not created. The output is
        captured instead of streamed, so that the usage lines name the
        wrapper -- the help must not teach the invocations which
        bypass it.
        """
        executor = subprocess.Popen(
            self._tofu_command, cwd=self.project.path,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = executor.communicate()
        sys.stdout.write(USAGE_LINE.sub(
            'Usage: debops tofu', std_out.decode(errors='replace')))
        sys.stderr.write(std_err.decode(errors='replace'))
        return executor.returncode

    def execute(self, capture=False):
        """Run the operation with the hooks around it and the store
        cycled for the duration.

        The informational operations -- the help surfaces of OpenTofu
        -- run without the machinery of the wrapper. The view tree of
        the regular operations is created lazily: the first command in
        a project without it applies the template and proceeds. The
        resolved provider set is recorded in the view's configuration
        drop-in, which drives the generated 'providers.tf' from then
        on; the binary which the operation runs is resolved after the
        view exists, from the version the view pins.

        When *capture* is set, the stdout of the operation is
        collected instead of streamed: the consumer reads the
        machine-readable output of the command -- 'output -json' of
        the inventory bridge -- whose content must not reach the
        terminal. The diagnostics still stream on stderr.

        Returns the exit code of the tofu subprocess, or the tuple of
        the exit code and the collected output when *capture* is set.
        """
        if self._informational:
            return self._run_informational()

        if not os.path.exists(os.path.join(self._view_root, 'main.tf')):
            create_view(self.project, self.project.view,
                        providers=resolve_providers(self.project,
                                                    self._providers),
                        modules=resolve_modules(self.project,
                                                self._modules))
        # The binary is resolved after the view exists: a freshly
        # created view carries its seeded version, which the managed
        # binary runs when it is installed
        self._tofu_command[0] = self._resolve_binary()

        hook_env = self._subprocess_env(self._tofu_env)
        if not run_hooks(self.project.path,
                         'pre-tofu-' + self._operation,
                         env=hook_env):
            raise ChildProcessError('Hook pre-tofu-{} aborted, not '
                                    'executing the OpenTofu command'.format(
                                        self._operation))

        rc = 0
        collected = None
        unlocked = False
        try:
            unlocked = self._unlock_secrets()

            if not self._operation_allowed():
                raise ChildProcessError(
                    "The operation '{}' is not among the operations "
                    "the 'operations' option of the 'tofu' section "
                    'allows the wrapper to run.'.format(self._operation))

            if self._operation in STATE_OPERATIONS:
                self._check_state_presence()
            if self._operation in LOCK_OPERATIONS:
                self._check_state_lock()
            self._check_approval()

            if self._plan_saved:
                os.makedirs(os.path.join(self._view_root, PLAN_DIR),
                            exist_ok=True)
            executor = subprocess.Popen(
                self._tofu_command, cwd=self._view_root,
                stdout=subprocess.PIPE if capture else None,
                env=self._subprocess_env(self._extra_env()))
            std_out, std_err = executor.communicate()
            rc = executor.returncode
            if capture:
                collected = std_out.decode()

            if self._plan_saved and rc == 0:
                self._announce_saved_plan()
                self._prune_plans()

        except KeyboardInterrupt:
            logger.notice('OpenTofu execution interrupted by user',
                          extra={'allow': 'syslog'})
            raise SystemExit('... aborted by user')

        else:
            self._ring_bell()

        finally:
            if unlocked:
                self._lock_secrets()

        run_hooks(self.project.path, 'post-tofu-' + self._operation,
                  extra_env={'DEBOPS_RETURN_CODE': rc},
                  env=self._subprocess_env(self._tofu_env))

        if capture:
            return rc, collected
        return rc

    def eval(self):
        """Return the shell commands which run the tofu operation.

        The runner-owned environment assignments prefix the command, so
        that the line is shell-copyable. The store's environment file
        carries the state passphrase of the view: its values are secret
        and are not part of the returned line -- they reach the tofu
        subprocess only, at execution time. The binary is resolved
        against the view's recorded version, which the command carries.
        """
        self._tofu_command[0] = self._resolve_binary()
        assignments = ['{}={}'.format(key, shlex.quote(value))
                       for key, value in sorted(self._tofu_env.items())]
        return ' '.join(assignments + [shlex.join(self._tofu_command)])
