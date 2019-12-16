# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class Error(Exception):
    """ Base error that serves as a parent for all other errors. """


class HttpError(Error):
    """ Error that signals failure in HTTP connection. """


class SyncError(Error):
    """ Error that signals failure when syncing state with remote. """


class SensuError(Error):
    """ Error that signals problems with Sensu Go web API. """


class BonsaiError(Error):
    """ Error that signals problems with Bonsai assets. """
