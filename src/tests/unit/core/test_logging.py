# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the package-level logging facilities: the project
context and its rendering in the journal records."""

import logging

import pytest

from debops import (ProjectContextFilter, ProjectFormatter,
                    get_project_context, set_project_context)


@pytest.fixture
def project_context():
    """Set a project context for the test and clear it afterwards, so
    that the context does not leak into other tests."""
    set_project_context("infra", "prod")
    yield
    set_project_context(None, None)


def make_record(message="the message", level=logging.NOTICE):
    return logging.LogRecord("debops.test", level, __file__, 1, message,
                             (), None)


def test_set_project_context_formats_the_tag():
    set_project_context("infra", "prod")
    try:
        assert get_project_context() == "infra:prod"
    finally:
        set_project_context(None, None)


def test_project_context_is_cleared():
    set_project_context(None, None)
    assert get_project_context() is None


def test_filter_stamps_records_with_the_context(project_context):
    record = make_record()
    ProjectContextFilter().filter(record)

    assert record.project_view == "infra:prod"


def test_filter_stamps_an_empty_tag_outside_of_a_context():
    set_project_context(None, None)
    record = make_record()
    ProjectContextFilter().filter(record)

    assert record.project_view == ""


def test_formatter_prefixes_records_inside_a_context(project_context):
    record = make_record()
    ProjectContextFilter().filter(record)
    formatter = ProjectFormatter("[%(levelname)s] %(message)s")

    rendered = formatter.format(record)

    assert rendered == "[NOTICE] [infra:prod] the message"


def test_formatter_leaves_records_outside_a_context_unchanged():
    set_project_context(None, None)
    formatter = ProjectFormatter("[%(levelname)s] %(message)s")

    rendered = formatter.format(make_record())

    assert rendered == "[NOTICE] the message"


def test_formatter_prefix_does_not_leak_into_other_handlers(project_context):
    """The prefix is folded into a copy of the record: a handler
    formatted before or after the journal handler must not see it."""
    record = make_record()
    ProjectContextFilter().filter(record)
    plain = logging.Formatter("%(message)s")

    journal_rendered = ProjectFormatter("%(message)s").format(record)
    other_rendered = plain.format(record)

    assert journal_rendered == "[infra:prod] the message"
    assert other_rendered == "the message"


def test_formatter_prefixes_formatted_messages(project_context):
    """Records formatted with '%s'-style arguments render the same
    text as their un-prefixed rendering, with the prefix in front."""
    record = logging.LogRecord("debops.test", logging.NOTICE, __file__, 1,
                               "value: %s", ("42",), None)
    ProjectContextFilter().filter(record)
    formatter = ProjectFormatter("[%(levelname)s] %(message)s")

    rendered = formatter.format(record)

    assert rendered == "[NOTICE] [infra:prod] value: 42"
