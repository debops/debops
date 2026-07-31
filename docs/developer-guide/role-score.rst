.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _role_score:

Role Quality Score
==================

The ``debops-role-score`` script grades every DebOps role against the
project's quality rules and makes CI fail on changes that drag a role's score
below the gate. Read this before working on a role — the detail output tells
you exactly what to fix.

.. contents::
   :local:
   :depth: 2


How scoring works
-----------------

The script lives at :file:`bin/debops-role-score` and depends only on PyYAML.
It is deterministic: the same repository state always produces the same
scores — the property a CI gate needs.

Each rule inspects one role and returns four values:

``weight``
  How much the rule is worth. Defaults come from ``DEFAULT_WEIGHTS``; you can
  override them with :command:`--weights` or set a weight to ``0`` to disable
  a rule.

``score``
  A value between ``0.0`` and ``1.0``, or negative for penalties — the
  ``role_era`` rule, for example, scores an early-era role ``-0.50``.

``max_score``
  ``1.0`` when the rule applies to the role, ``0.0`` when it is **not
  applicable** (N/A). N/A rules are excluded from the score entirely.

``detail``
  A short human-readable note explaining the result. This is the fastest way
  to find out *why* a rule scored the way it did; it shows up in
  :command:`--details` and :command:`--verbose` output and in the JSON.

The overall score is the weighted sum of the applicable rules divided by
their total weight, scaled to a ``0``--``10`` range:

.. code-block:: text

   overall = weighted_sum / total_weight * 10

A rule counts toward ``total_weight`` only when it applies. A role with no
applicable rules scores ``0``.

The score ceiling
~~~~~~~~~~~~~~~~~

A perfect role would score ``10``, but the rules do not let it. The era rules
reward contradictory lifecycles: a role cannot be both written in the
Universal Configuration era *and* stable since 2015, so ``role_era``,
``role_modernization``, ``role_stability`` and ``modern_stability`` can never
all pay out at once. The script computes the highest achievable score — the
**ceiling** — from the current rule weights every time you ask:

.. code-block:: console

   bin/debops-role-score --ceiling

The ceiling changes whenever rules or weights change, so there is no
hardcoded number to keep in sync. The CI gate is defined as a fraction of it
(see :ref:`The CI gate <role_score_ci_gate>` below).

Design eras
~~~~~~~~~~~

Three rules key off the first copyright year of the role, which groups roles
into design eras:

.. list-table::
   :widths: 20 25 55
   :header-rows: 1

   * - Era
     - First copyright year
     - ``role_era`` score
   * - early
     - before 2017
     - ``-0.50``
   * - exploration
     - 2017--2020
     - ``0.00``
   * - Universal Configuration
     - 2021 and later
     - ``+0.50``

The newest era takes its name from the variable syntax the project
standardized on — see :ref:`universal_configuration`. Roles written since
2021 are expected to be built around that pattern, so ``role_era`` treats
them as the baseline. Run :command:`--details` and the era row reads
``Universal Configuration (2021)`` — the year in parentheses is the first
copyright year the rule found.

The other era rules fine-tune this:

- ``role_modernization`` rewards an early-era role that was substantially
  rewritten during the Universal Configuration era;
- ``modern_stability`` rewards a post-2022 role with low commit churn;
- ``role_stability`` is the inverse: an early-era role that barely needed
  changes for years.

No role can collect all three, which is why the ceiling sits below ``10``.


Reading your role's score
-------------------------

Start with your role and the full rule breakdown:

.. code-block:: console

   bin/debops-role-score --roles samba --details

You get one line per rule: the weight, the score earned, and the detail note.
Rows prefixed with ``[N/A]`` do not apply to this role and are irrelevant.
Rules that hurt — the negative ones — stand out, and the detail text says why
they fired.

The default output without :command:`--details` is a compact scoreboard
sorted by score, with the role count, average and median. To score the whole
fleet, :command:`make role-score` prints that scoreboard and
:command:`make role-score-verbose` adds the per-rule breakdown. To compare a
few roles:

.. code-block:: console

   bin/debops-role-score --roles samba,gitlab,tor --details

Other output modes:

- :command:`--verbose` shows only the rules that actually matter
  (``|weight * score| >= 0.10``), skipping N/A and negligible rows. This is
  what CI runs use, so pull request logs stay short.
- :command:`--full` prints one column per rule; :command:`--csv` mirrors it.
- :command:`--json` emits the full per-rule breakdown, ready for jq.
- :command:`--rule LIST` restricts the run to specific rules, handy when you
  are fixing one thing and want to check it in isolation.

To try a rule at a different weight without editing the script, use a weights
file:

.. code-block:: yaml

   ---
   weights:
     variable_naming: 0.5
     docs_presence: 0.0
   skip_roles:
     - experimental_role

Setting a weight to ``0`` disables the rule; roles listed in ``skip_roles``
are not scored.


What the rules reward
---------------------

The full rule reference lives in the script itself — run
:command:`debops-role-score --list-rules` to see every rule with its current
weight and a one-line description. The same rules, grouped by theme:

Variables and naming
~~~~~~~~~~~~~~~~~~~~

The heaviest part of the score. Variables must use the ``<role>__`` prefix
(``variable_naming``), full three-level scoping with ``__group_`` and
``__host_`` overrides (``scoped_variables``), the ``__combined_`` merge
pattern (``combined_variables``), and the ``parse_kv_items`` filter for
structured values (``parse_kv_items_usage``). ``dependent_variables`` rewards
the ``__dependent_`` pattern and pays a bonus when other roles reference your
variables.

Tasks
~~~~~

Task conditionals (``when:``, ``changed_when:``, ``failed_when:``,
``until:``) must resolve to booleans: the ``| d()`` / ``| default()``
filter returns the raw value and breaks Ansible 2.19+, so it is penalized
(``default_filter_usage``) and the ``is defined`` / ``is truthy`` tests are
rewarded (``is_truthy_usage``). Tasks load includes through ``task_src`` and
templates through ``template_src``, and carry ``role::<name>`` /
``skip::<name>`` tags (``task_tags``). Task files are split by concern instead
of one big ``main.yml`` (``task_file_organization``), and small roles with up
to three tasks and no templates are exempt from these structural rules
entirely — there is nothing to reorganize yet.

Templates and files
~~~~~~~~~~~~~~~~~~~

Templates carry SPDX license headers (``spdx_headers``), render
``{{ ansible_managed }}`` (``ansible_managed``), use ``| d()`` defaults
(``template_default_filter``), and build fact files at runtime instead of
hardcoding values (``fact_runtime_detection``). Static ``files/`` directories
are penalized (``files_directory_absent``) — ship a template instead — and
hardcoded ``/etc/`` or ``/var/`` paths in templates are a penalty
(``hardcoded_paths``).

Metadata and packaging
~~~~~~~~~~~~~~~~~~~~~~

``meta/main.yml`` must exist (``missing_meta``), declare the
``debops.debops`` collection (``collections_declared``), list explicit
platforms (``meta_platforms_specific``) and galaxy tags
(``galaxy_tags_present``), and carry a ``dependencies: []`` entry
(``dependencies_empty``). The legacy ``vars/`` directory costs you points
(``legacy_vars_dir``).

Facts
~~~~~

Roles that use local facts keep them in a template with a shebang
(``local_facts``), run ``flush_handlers`` after writing them
(``flush_handlers``), and reference ``ansible_local`` in their ``when:``
clauses (``ansible_local_in_conditions``). Static JSON fact files are a
penalty (``static_json_facts``).

Lifecycle and documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beyond the era rules, ``foundational`` rewards roles that other roles
reference through their variables, and ``collection_excluded`` penalizes
roles that are deliberately omitted from the Collection build. Finally,
``docs_presence`` checks that the role has real ``getting-started.rst``
documentation — short placeholder pages score near zero.


Making your role pass
---------------------

In order:

1. **Score first.** Run
   ``bin/debops-role-score --roles <name> --details`` and read the detail
   notes. The penalty rows and the missing big-ticket rules are your list.
2. **Fix the heavy hitters.** Start with the highest weights — variable
   scoping, facts, documentation — not the 0.1-weight niceties. A change to
   a 1.0-weight rule moves the score ten times as far as a 0.1 one.
3. **Re-run and compare.** The compact scoreboard shows the average and
   median, so you can tell whether your role is above or below the pack. The
   script is deterministic: if the score moved, the role changed.
4. **Leave N/A alone.** If a row is ``[N/A]``, the rule does not apply — do
   not add fake structure to a role that is too small to need it.

Two common surprises:

- **Missing documentation.** ``docs_presence`` looks at body lines in
  :file:`docs/ansible/roles/<name>/getting-started.rst`. A stub of a few
  sentences scores almost nothing; write the doc properly and the rule
  mostly pays out.
- **Collection exclusion.** If the role is not shipped in the Collection, it
  pays a fixed 1.5 penalty. Being in the Collection is usually the right
  answer; if the exclusion is deliberate, accept the cost.

The CI gate judges *changed* roles only. A legacy role that is never touched
passes by default; touch it, and the change has to hold the gate.


.. _role_score_ci_gate:

The CI gate
-----------

The :file:`.github/workflows/role-score.yml` workflow runs on every push and
pull request. It detects which roles the change touched, scores just those
roles, and fails the build if any of them lands below the gate.

The workflow defines the gate as a fraction of the score ceiling, computed
from the current rule weights at run time:

.. code-block:: console

   bin/debops-role-score --roles <changed-roles> --min-score-fraction 0.40 --verbose

The 40% bar is deliberately low: it stops the worst offenders and prevents
regressions without demanding a full modernization of every role on day one.
Because the fraction is applied to the live ceiling, adding or reweighting a
rule automatically re-derives the gate — there is nothing to recompute by
hand.

For local runs:

- :command:`--min-score-fraction 0.40` gates at 40% of the current ceiling;
- :command:`--min-score 4.0` gates at a fixed absolute score instead, and
  takes precedence if both are given;
- :command:`--ceiling` prints the current ceiling and gate value, so you can
  see what fraction means what on any given day.


Reporting flags
---------------

The script attaches two non-scoring flags to each role. They never affect the
score, but they tell you how the role is wired into the fleet:

``common``
  The role runs on every host via
  :file:`ansible/playbooks/layer/common.yml`.

``no-service-playbook``
  No service playbook for the role exists under
  :file:`ansible/playbooks/service/`.

Flags appear as a ``[common]``-style suffix in the compact and detailed
outputs, in a ``Flags`` column in :command:`--full` and :command:`--csv`
output, and as a ``flags`` array in JSON. A role that runs on every host
deserves more scrutiny than one deployed on demand. Find them with:

.. code-block:: console

   bin/debops-role-score --json | jq -r '.[] | select(.flags | index("common")) | "\(.name)\t\(.overall)"'


See also
--------

- :ref:`universal_configuration` for the variable syntax that defines the
  newest design era
- :ref:`testing` for the other validation the project runs
- :ref:`contributing_docs` for documentation contribution conventions
