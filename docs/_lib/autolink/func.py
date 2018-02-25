# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 DebOps project https://debops.org/

from docutils import nodes


def setup(app):
    app.add_role('man', autolink('https://manpages.debian.org/%s'))


def autolink(pattern):
    def role(name, rawtext, text, lineno, inliner, options={}, content=[]):
        url = pattern % (text,)
        node = nodes.reference(rawtext, text, refuri=url, **options)
        return [node], []
    return role
