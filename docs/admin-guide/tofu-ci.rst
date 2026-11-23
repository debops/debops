.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _tofu_ci:

OpenTofu in CI pipelines
========================

.. contents::
   :local:

Running plan and apply from a pipeline is the standard way to keep a
fleet honest: plan on every merge request, apply on merge. The
wrapper fits the shape with one constraint: the
one-step apply refuses to run non-interactively, by design. The
pipeline therefore works with saved plan files. The job which
produces a plan file carries the review, so the file is pre-approved
by construction. It applies without an approval prompt.

The plan files are self-contained. OpenTofu encrypts them with the
view's stanza, they read no state, and they capture the backend
configuration of the plan job. That makes them clean CI artifacts:
plan in one job, upload the file, apply it in another.


What the pipeline needs
-----------------------

The pipeline needs the same things a controller needs, in a form CI
systems accept:

- The project checkout with the committed view configuration and the
  provider lock file.
- The unlocked store. For a git-crypt store, export the repository
  key and carry it as a protected CI variable. The pipeline unlocks
  before the first wrapper run. The state passphrase rides in the
  store's :file:`secret/environment` file, so unlocking the store
  releases everything.
- The OpenTofu binary. :command:`debops tofu install` works in a
  pipeline and pins the version the view records.
- For a remote backend, the state credentials. A GitLab pipeline
  authenticates to its own state endpoint with the job token: the
  username is :literal:`gitlab-ci-token` and the password is
  :literal:`$CI_JOB_TOKEN`. Supply them as the ``TF_HTTP_USERNAME``
  and ``TF_HTTP_PASSWORD`` environment variables instead of a
  :file:`backend.conf`, and the checkout needs no state credentials
  at all.


The recipe
----------

**Plan job.** Plan with the detailed exit code and upload the saved
plan file:

.. code-block:: console

   alice@controller:~$ debops tofu -V <view> plan -detailed-exitcode

The exit code is 0 with no changes, 2 with changes and 1 on failure.
The pipeline can skip the apply job when the plan is empty. The saved
plan file lands in the view's :file:`plans/` directory with its
sequence id in the name. Publish it as the job artifact.

**Review.** The merge request carries the plan summary. A reviewer
who wants the full diff runs :command:`debops tofu -V <view> plans
show <id>` locally against the downloaded artifact -- the plan file is
readable without the state.

**Apply job.** On merge, download the artifact and apply it by path:

.. code-block:: console

   alice@controller:~$ debops tofu -V <view> apply plans/debops-<stamp>.tfplan

The apply runs without an approval prompt and holds the remote lock
for its duration. A concurrent apply to the same state waits or
refuses, which is the concurrency control the pipeline does not have
to reimplement.


What the wrapper adds in CI
---------------------------

The state checks work the same way they do locally. The wrapper
refuses a view whose state is missing from the unlocked store, with
:literal:`--allow-missing-state` as the deliberate way out. In a
pipeline this catches the common failure of a job that lost the store
unlock and would otherwise plan to recreate the whole fleet.

The backend-change and stale-data-directory failures name their way
out on stderr, and the job log carries it. The retention prunes the
plan files on the controller, not in the pipeline. The artifact
retention of the CI system governs the pipeline copies.

The recipe deliberately stops at the raw passthrough for the apply.
A first-class CI integration, with the wrapper driving the pipeline
itself, waits for an audience that needs it. The artifact flow uses
only the surfaces the wrapper already has.
