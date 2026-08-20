# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import os
import logging

from xdg.BaseDirectory import xdg_config_home

logger = logging.getLogger(__name__)

# Default timeout for hook scripts in seconds (5 minutes)
DEFAULT_HOOK_TIMEOUT = 300


def _discover_hooks(hook_dir):
    """Discover executable scripts in a hooks directory.

    Returns a sorted list of absolute paths to executable files.
    Non-executable files and directories are silently skipped.
    """
    scripts = []
    if not os.path.isdir(hook_dir):
        return scripts

    for entry in sorted(os.listdir(hook_dir)):
        entry_path = os.path.join(hook_dir, entry)
        if not os.path.isfile(entry_path):
            continue
        if not os.access(entry_path, os.X_OK):
            continue
        scripts.append(os.path.abspath(entry_path))

    return scripts


def run_hooks(project_path, hook_name, timeout=DEFAULT_HOOK_TIMEOUT):
    """Run all executable scripts for a given hook name.

    Searches for scripts in two locations, in priority order:

      1. <project_path>/.debops/hooks/<hook_name>/  (project-local)
      2. ~/.config/debops/hooks/<hook_name>/        (user-global)

    Scripts from the project-local directory run first, followed by
    user-global scripts. Within each directory, scripts run in sorted
    order (use numeric prefixes like 00-, 99- for deterministic ordering).

    Each hook script receives the following environment variables:

      DEBOPS_HOOK_NAME    - name of the hook being executed
      DEBOPS_PROJECT_PATH - path to the project directory

    The script inherits the full process environment, which includes
    all DebOps-configured variables (DEBOPS_ANSIBLE_COLLECTIONS_PATH,
    ANSIBLE_CONFIG, etc.).

    Args:
        project_path: Absolute path to the DebOps project directory.
        hook_name: Name of the hook point (e.g. 'pre-run', 'post-lock').
        timeout: Maximum seconds to wait for each script. Default: 300.

    Returns:
        True if all hooks executed successfully (exit code 0).
        False if any hook failed (non-zero exit code).
        True if no hooks were found (no-op).
    """
    project_hooks_dir = os.path.join(project_path, '.debops', 'hooks',
                                     hook_name)
    user_hooks_dir = os.path.join(xdg_config_home, 'debops', 'hooks',
                                  hook_name)

    project_scripts = _discover_hooks(project_hooks_dir)
    user_scripts = _discover_hooks(user_hooks_dir)

    all_scripts = project_scripts + user_scripts

    if not all_scripts:
        return True

    logger.debug('Found {} hook script(s) for "{}"'.format(
        len(all_scripts), hook_name))

    hook_env = os.environ.copy()
    hook_env['DEBOPS_HOOK_NAME'] = hook_name
    hook_env['DEBOPS_PROJECT_PATH'] = os.path.abspath(project_path)

    for script in all_scripts:
        logger.notice('Running hook script: {}'.format(script),
                      extra={'block': 'stderr'})
        try:
            result = subprocess.run(
                [script],
                cwd=os.path.abspath(project_path),
                env=hook_env,
                timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.error('Hook script {} timed out after {} seconds'.format(
                script, timeout), extra={'block': 'stderr'})
            return False

        if result.returncode != 0:
            logger.error('Hook script {} failed with exit code {}'.format(
                script, result.returncode), extra={'block': 'stderr'})
            return False

    return True
