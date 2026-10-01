# Custom Sphinx translator for manual page output
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from docutils import nodes

from sphinx.writers.manpage import ManualPageTranslator


class ManPagesTranslator(ManualPageTranslator):
    """Custom man page translator.

    Changes compared to the Sphinx default:

    - the ``.. contents::`` table of contents rendered by the default
      translator is a plain bullet list with no navigation value in
      a manual page, so it is skipped entirely
    """

    def visit_topic(self, node):
        if 'contents' in node.get('classes', []):
            raise nodes.SkipNode
        super().visit_topic(node)


def setup(app):
    app.set_translator('man', ManPagesTranslator)
