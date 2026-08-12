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
    - literal blocks are emitted with ``.nf`` (no-fill) which means groff
      will not wrap long lines; lines are hard-wrapped here so that they
      fit in a standard 80 column terminal
    """

    def __init__(self, document, builder):
        super().__init__(document, builder)
        self._in_literal_block = False

    def visit_topic(self, node):
        if 'contents' in node.get('classes', []):
            raise nodes.SkipNode
        super().visit_topic(node)

    def visit_literal_block(self, node):
        self._in_literal_block = True
        super().visit_literal_block(node)

    def depart_literal_block(self, node):
        self._in_literal_block = False
        super().depart_literal_block(node)

    def visit_Text(self, node):
        if self._in_literal_block:
            text = node.astext()
            wrapped = '\n'.join(
                self._wrap_line(line) for line in text.split('\n')
            )
            node = nodes.Text(wrapped)
        super().visit_Text(node)

    def _wrap_line(self, line):
        """Hard-wrap *line* to the available terminal width."""
        width = max(1, int(78 - sum(self._indent)))
        if len(line) <= width:
            return line
        indent = line[:len(line) - len(line.lstrip())]
        wrapped = []
        current = ''
        for word in line[len(indent):].split():
            candidate = word if not current else current + ' ' + word
            if len(candidate) <= width:
                current = candidate
            else:
                if current:
                    wrapped.append(current)
                if len(word) > width:
                    while len(word) > width:
                        wrapped.append(word[:width])
                        word = word[width:]
                current = indent + word
        if current:
            wrapped.append(current)
        return '\n'.join(wrapped)


def setup(app):
    app.set_translator('man', ManPagesTranslator)
