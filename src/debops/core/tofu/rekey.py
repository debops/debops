# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The state passphrase rotation of an OpenTofu view.

The 'debops tofu rekey' operation rotates the encryption passphrase
through the fallback mechanism of the OpenTofu encryption: the key
provider the state envelope references becomes the fallback, the
new primary takes the next generation label, and the state
re-encrypts on the next write. The rotation rewrites the
encryption block of the view configuration per phase -- the
fallback inherits the label the envelope's metadata references,
a renamed fallback finds no metadata and the state reads as
keyless -- and every interruption short of the final cleanup
leaves a recoverable state that a re-run resumes by its markers.
"""

import logging
import os
import re

from ..secrets import (environment_path, environment_values,
                       passphrase_length, random_passphrase,
                       unlocked_store)
from .changes import file_change
from .plans import remove_saved
from .registry import view_tofu_root
from .runner import TofuOperationFailed, \
    run_tofu_operation
from .secrets import TofuSecretStore
from ..utils import write_file

logger = logging.getLogger(__name__)

# The rekey surgery: the encryption block of the view is rewritten
# per rotation phase. The fallback key provider inherits the label
# the state envelope's metadata references -- the decryption looks
# the provider up by that label, a renamed fallback finds no
# metadata and the state reads as keyless -- and the new primary
# takes the next generation label: 'state' rotates to 'state-2',
# 'state-2' to 'state-3'.

REKEY_ENCRYPTION_ROTATED = """  encryption {{
    key_provider "pbkdf2" "{fallback}" {{
      passphrase = var.old_state_passphrase
    }}

    method "aes_gcm" "{fallback}" {{
      keys = key_provider.pbkdf2.{fallback}
    }}

    key_provider "pbkdf2" "{primary}" {{
      passphrase = var.state_passphrase
    }}

    method "aes_gcm" "{primary}" {{
      keys = key_provider.pbkdf2.{primary}
    }}

    state {{
      method   = method.aes_gcm.{primary}
      fallback {{
        method = method.aes_gcm.{fallback}
      }}
      enforced = true
    }}

    plan {{
      method = method.aes_gcm.{primary}
    }}
  }}
"""

REKEY_ENCRYPTION_CLEAN = """  encryption {{
    key_provider "pbkdf2" "{primary}" {{
      passphrase = var.state_passphrase
    }}

    method "aes_gcm" "{primary}" {{
      keys = key_provider.pbkdf2.{primary}
    }}

    state {{
      method   = method.aes_gcm.{primary}
      enforced = true
    }}

    plan {{
      method = method.aes_gcm.{primary}
    }}
  }}
"""

REKEY_OLD_STATE_VAR = """
variable "old_state_passphrase" {
  type      = string
  sensitive = true
}
"""


def _encryption_block(main_tf):
    """The encryption block of the view configuration: from the
    'encryption {' line to its matching closing brace, None when the
    configuration carries none."""
    lines = main_tf.splitlines(keepends=True)
    start = None
    depth = 0
    for index, line in enumerate(lines):
        if start is None:
            if line.strip() == 'encryption {':
                start = index
                depth = line.count('{') - line.count('}')
            continue
        depth += line.count('{') - line.count('}')
        if depth == 0:
            return ''.join(lines[start:index + 1])
    return None


def _primary_label(block):
    """The label of the key provider the state stanza encrypts
    with: the first method reference in the encryption block, the
    state stanza's."""
    match = re.search(r'method\s*=\s*method\.aes_gcm\.([A-Za-z0-9_-]+)',
                      block)
    if match is None:
        raise ValueError(
            'The encryption block of the view carries no state '
            'encryption method: the rekey cannot rotate it')
    return match.group(1)


def _fallback_label(block):
    """The label of the fallback key provider, None when the block
    carries no fallback -- the shape of a view which is not mid-
    rotation."""
    match = re.search(r'fallback \{[^}]*method\s*=\s*method\.aes_gcm\.'
                      r'([A-Za-z0-9_-]+)', block)
    return match.group(1) if match else None


def _next_primary_label(label):
    """The label of the key provider the rotated state encrypts
    under: the next generation of the current one."""
    stem, separator, generation = label.rpartition('-')
    if separator and generation.isdigit():
        return stem + '-' + str(int(generation) + 1)
    return label + '-2'


def _rekey_env_path(view_root):
    """The environment file of the view's store."""
    return environment_path(view_root)


def _rekey_env_value(view_root, key):
    """One TF_VAR_* value of the environment file, None when the key
    is not there."""
    path = _rekey_env_path(view_root)
    if not os.path.exists(path):
        return None
    return environment_values(view_root).get(key)


def _rekey_env_write(project, view_root, passphrase,
                     old_passphrase=None):
    """Rewrite the 'TF_VAR_state_passphrase' line of the environment
    file, carrying or dropping the old-passphrase marker; the user's
    own keys in the file are preserved line-for-line."""
    path = _rekey_env_path(view_root)
    with open(path) as handle:
        lines = handle.read().splitlines()
    kept = [line for line in lines
            if not line.startswith('TF_VAR_state_passphrase=')
            and not line.startswith('TF_VAR_old_state_passphrase=')]
    kept.append('TF_VAR_state_passphrase=' + passphrase)
    if old_passphrase is not None:
        kept.append('TF_VAR_old_state_passphrase=' + old_passphrase)
    write_file(path, '\n'.join(kept) + '\n', overwrite=True,
               project=project.path)


def rekey_view(project, view, workspace=None):
    """Rotate the state passphrase of a view.

    The rotation uses OpenTofu's encryption fallback, the mechanism
    the state migration exercised: the key provider the state
    envelope references becomes the fallback -- its label is
    inherited, the envelope's metadata is looked up by it -- and
    the new primary takes the next generation label. The refresh
    re-encrypts the state under the new primary, the verification
    plan reads the state with the new passphrase alone, and the
    cleanup removes the fallback and the old variable. Every
    interruption short of the final cleanup leaves a recoverable
    state -- a re-run resumes by the markers, the fallback block in
    the encryption stanza and the old-passphrase variable in the
    environment file. The encryption block is rewritten per phase:
    hand-modifications inside it do not survive the rotation.

    The saved plan files are removed and announced: they are
    encrypted under the retired key and the plan stanza carries no
    fallback. The named workspaces carry separate state files and
    need a rekey each. Returns True when the rotation completed.
    """
    view_root = view_tofu_root(project, view)
    records = []
    main_tf_path = os.path.join(view_root, 'main.tf')
    with open(main_tf_path) as handle:
        main_tf = handle.read()

    block = _encryption_block(main_tf)
    if block is None:
        raise ValueError(
            'The view configuration of {!r} carries no encryption '
            'block: the rekey cannot rotate it'.format(view))
    primary = _primary_label(block)
    fallback = _fallback_label(block)
    resuming = (fallback is not None
                or _rekey_env_value(
                    view_root, 'TF_VAR_old_state_passphrase')
                is not None)

    store = TofuSecretStore(project, view)
    with unlocked_store(store):
        old_passphrase = _rekey_env_value(
            view_root, 'TF_VAR_old_state_passphrase')
        new_passphrase = _rekey_env_value(
            view_root, 'TF_VAR_state_passphrase')
        if old_passphrase is None:
            # A fresh rotation: the old passphrase is the current one
            if new_passphrase is None:
                raise ValueError(
                    "The environment file of the view {!r} carries "
                    "no 'TF_VAR_state_passphrase': the state "
                    'encryption cannot be rotated'.format(view))
            old_passphrase = new_passphrase
            new_passphrase = random_passphrase(passphrase_length(project))

        # The environment carries the new primary and the old
        # fallback for as long as the rotation runs
        _rekey_env_write(project, view_root, new_passphrase,
                         old_passphrase)

    # The rotation phase: the fallback inherits the label the state
    # envelope references, the new primary takes the next generation
    next_primary = _next_primary_label(primary)
    previous_main_tf = main_tf
    main_tf = main_tf.replace(
        block,
        REKEY_ENCRYPTION_ROTATED.format(fallback=primary,
                                        primary=next_primary))
    if REKEY_OLD_STATE_VAR not in main_tf:
        state_var = ('variable "state_passphrase" {\n'
                     '  type      = string\n  sensitive = true\n}')
        main_tf = main_tf.replace(
            state_var, state_var + REKEY_OLD_STATE_VAR)
    write_file(main_tf_path, main_tf, overwrite=True,
               project=project.path)
    records.append(file_change(main_tf_path, 'update',
                               previous_main_tf, main_tf,
                               project.path))
    records.append(file_change(_rekey_env_path(view_root), 'update',
                               None, None, project.path, secret=True))

    # The re-encryption: the state reads through the fallback, writes
    # under the new primary
    run_tofu_operation(project, ['refresh'], workspace=workspace)

    # The cleanup phase: the block without the fallback, the old
    # variable out of the configuration -- the old passphrase stays
    # in the environment until the verification passes
    with open(main_tf_path) as handle:
        main_tf = handle.read()
    previous_main_tf = main_tf
    block = _encryption_block(main_tf)
    main_tf = main_tf.replace(
        block, REKEY_ENCRYPTION_CLEAN.format(primary=next_primary))
    main_tf = main_tf.replace(REKEY_OLD_STATE_VAR, '')
    write_file(main_tf_path, main_tf, overwrite=True,
               project=project.path)
    records.append(file_change(main_tf_path, 'update',
                               previous_main_tf, main_tf,
                               project.path))

    # The verification: the state reads with the new passphrase alone
    verification_error = None
    try:
        run_tofu_operation(project, ['plan'], workspace=workspace)
    except TofuOperationFailed as errmsg:
        verification_error = str(errmsg)
    if verification_error is not None:
        # The verification failed: the rotation phase goes back in,
        # the state stays readable through the fallback
        with open(main_tf_path) as handle:
            main_tf = handle.read()
        block = _encryption_block(main_tf)
        main_tf = main_tf.replace(
            block,
            REKEY_ENCRYPTION_ROTATED.format(fallback=primary,
                                            primary=next_primary))
        if REKEY_OLD_STATE_VAR not in main_tf:
            state_var = ('variable "state_passphrase" {\n'
                         '  type      = string\n  sensitive = true\n}')
            main_tf = main_tf.replace(
                state_var, state_var + REKEY_OLD_STATE_VAR)
            write_file(main_tf_path, main_tf, overwrite=True,
                       project=project.path)
        raise ChildProcessError(
            "The verification plan of the view {!r} failed ({}): "
            'the rotation phase is back in place, the old passphrase '
            'is still in the environment file -- investigate before '
            'the cleanup runs.'.format(view, verification_error))

    # The cleanup: the old variable out of the environment, the
    # old-key plan files removed
    _rekey_env_write(project, view_root, new_passphrase)
    records.append(file_change(_rekey_env_path(view_root), 'update',
                               None, None, project.path, secret=True))
    for path in remove_saved(view_root):
        records.append(file_change(os.path.join(view_root, path),
                                   'remove', None, None,
                                   project.path, secret=True))
        logger.notice(
                "Removed the plan file '{}' of the view {!r}: the "
                'plan is encrypted under the retired '
                'passphrase'.format(path, view),
                extra={'allow': ['stderr', 'syslog']})

    logger.notice(
        'The state passphrase of the view {!r} in project {!r} is '
        'rotated: the state reads with the new passphrase, the '
        'fallback is removed'.format(view, project.name),
        extra={'allow': ['stderr', 'syslog']})
    return records
