.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _tofu_state_adoption:

Adopting infrastructure and rotating passphrases
================================================

.. contents::
   :local:

Two situations share one mechanism: the OpenTofu encryption fallback
chain. The first brings an existing fleet into a fresh DebOps view.
The second rotates the state passphrase of a view that already has
one.


Why not import blocks
---------------------

OpenTofu's import mechanism looks like the natural adoption path, and
for many providers it is. For the Incus provider it is not: the
import leaves the ``image`` attribute unpopulated, so every
``incus_instance`` plans as *must be replaced*. A state-carrying
adoption avoids the problem entirely. The plan was clean on the
first try after the configuration alignment.

Before adopting, align the target view's configuration with what the
fleet actually runs. Infrastructure that someone changed out of band
(a container flag set by hand, an external update) plans as a change
until the configuration matches. Expect to adopt the out-of-band
settings into the configuration first.


The adoption recipe
-------------------

The idea: copy the encrypted state of the old view into the new one,
and let OpenTofu re-encrypt it under the new passphrase. The
envelope is opaque ciphertext. The copy needs no decrypt step.

**1. Teach the new view the old key.** In the new view's
:file:`main.tf`, add a key provider and a method for the retired
passphrase, and a fallback that uses them:

.. code-block:: text

   # tofu/views/<view>/main.tf
   variable "old_state_passphrase" {
     type      = string
     sensitive = true
   }

   terraform {
     encryption {
       key_provider "pbkdf2" "old" {
         passphrase = var.old_state_passphrase
       }
       method "aes_gcm" "old" {
         keys = key_provider.pbkdf2.old
       }
       method "aes_gcm" "new" {
         keys = key_provider.pbkdf2.state
       }
       state {
         method   = method.aes_gcm.new
         enforced = true
         fallback {
           method = method.aes_gcm.old
         }
       }
     }
   }

The old label must be the label the source view used: the encrypted
envelope's metadata references it, and a mismatched label fails the
lookup. If the source view configured non-default key provider
parameters (iterations, salt), replicate them in the fallback
provider.

**2. Carry the old passphrase in the store.** Unlock the store and
append the retired passphrase to the tracked
:file:`secret/environment` file, as the environment variable of the
declared variable: ``TF_VAR_old_state_passphrase=<value>`` for the
variable above. The wrapper passes ``TF_VAR_*`` keys only, and the
file is store-encrypted at rest.

**3. Copy the state.** Copy the source view's
:file:`state/terraform.tfstate` into the target view's. A plain file
copy does it: the envelope is opaque.

**4. Plan, align, apply.** Run :command:`debops tofu -V <view>
plan`. OpenTofu reads the state through the fallback and saves a
plan. Review it: expect no adds and no destroys. Adopt the
out-of-band settings into the configuration until the plan reads
*No changes*, then apply the saved plan. The apply writes the state,
and the write re-encrypts the envelope with the primary method.

**5. Remove the fallback.** Remove the old key provider, the old
method, the fallback stanza, the variable and the
``TF_VAR_*`` line. Run :command:`debops tofu -V <view> plan`. A *No changes* result
proves the new key decrypts alone.

**6. Commit.** The state lands in git as native OpenTofu ciphertext.
The configuration and the environment file commit as usual.

Two facts to keep straight. Only an apply re-encrypts the state. A
plan never writes state, so the rotation completes at the apply step. And ``enforced = true`` coexists with the fallback:
the stanza still refuses to ever write plaintext.


Rotating the passphrase with 'debops tofu rekey'
------------------------------------------------

For a view you own end to end, the rotation is one operation:

.. code-block:: console

   alice@controller:~$ debops tofu -V <view> rekey

The operation generates a new passphrase and edits the encryption
block of the view configuration through the phases of the rotation.
The fallback carries the retired key first, and the new primary takes
the next generation label. The cleanup returns the block to the
single-provider shape. The operation removes the plan files encrypted under the retired
key, which would be unreadable afterwards.

The label detail matters: the fallback key provider inherits the
label the state envelope's metadata references. A renamed fallback
finds no metadata, and the state reads as keyless. The operation
handles the labels for you. If you hand-roll a rotation, follow the
generation scheme (``state``, ``state-2``, ...).

An interrupted rotation leaves a recoverable state and a re-run
resumes by its markers. The state passphrase and the repository
share one trust domain. One typo in the environment file makes every
state written so far unreadable, which is why the operation exists
instead of a manual recipe. Keep a copy of the passphrase in a
password manager until the rotation completes.
