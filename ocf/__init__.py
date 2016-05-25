# This file is part of python-ocf.
# Copyright (C) 2015  Tiger Computing Ltd. <info@tiger-computing.co.uk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
**python-ocf: Open Clustering Framework Resource Agent API for Python**

This particular module mostly serves as a repository for constants used
extensively during OCF RA development, and contains short-cuts for accessing
the most important elements from sub-modules of this ``ocf`` package.

.. seealso::

   `The OCF Resource Agent Developer's Guide, Return codes`
      <http://www.linux-ha.org/doc/dev-guides/_return_codes.html>

In addition to the members declared below, the following aliases are available:

.. py:class:: ocf.ResourceAgent

   Alias for :class:`ocf.ra.ResourceAgent`.

.. py:class:: ocf.Parameter

   Alias for :class:`ocf.ra.Parameter`.

.. py:class:: ocf.Action

   Alias for :class:`ocf.ra.Action`.
"""

from __future__ import absolute_import

import logging

from ocf.version import __version__  # noqa

#: Resource agent exit code: The action completed successfully.
OCF_SUCCESS = 0

#: Resource agent exit code: The action returned a generic error.
OCF_ERR_GENERIC = 1

#: Resource agent exit code: The resource agent was invoked with incorrect
#: arguments.
OCF_ERR_ARGS = 2

#: Resource agent exit code: The resource agent was instructed to execute an
#: action that the agent does not implement.
OCF_ERR_UNIMPLEMENTED = 3

#: Resource agent exit code: The action failed due to insufficient permissions.
OCF_ERR_PERM = 4

#: Resource agent exit code: The action failed because a required component is
#: missing on the node where the action was executed.
OCF_ERR_INSTALLED = 5

#: Resource agent exit code: The action failed because the user misconfigured
#: the resource.
OCF_ERR_CONFIGURED = 6

#: Resource agent exit code: The resource was found not to be running.
OCF_NOT_RUNNING = 7

# Non-standard exit codes.
#
# OCF does not include the concept of master/slave resources so pacemaker needs
# to extend it so it can discover a resource's complete state.
#
# OCF_RUNNING_MASTER:
#    The resource is in "master" mode and fully operational
# OCF_FAILED_MASTER:
#    The resource is in "master" mode but in a failed state
#
# The extra two values should only be used during a probe.
#
# Probes are used to discover resources that were started outside of the CRM
# and/or left behind if the LRM fails. They can be identified in RA scripts by
# checking ocf.env.is_probe().
#
# Failed "slaves" should continue to use: OCF_ERR_GENERIC.
# Fully operational "slaves" should continue to use: OCF_SUCCESS.

#: Resource agent exit code: The resource was found to be running in the
#: ``Master`` role.
OCF_RUNNING_MASTER = 8

#: Resource agent exit code: The resource was found to have failed in the
#: ``Master`` role.
OCF_FAILED_MASTER = 9

#: :class:`logging.Logger` instance
log = logging.getLogger(__name__)

# Import these at the end so that the circular references don't go haywire
import ocf.environment  # noqa
from ocf.ra import ResourceAgent, Parameter, Action  # noqa

#: Singleton instance of :class:`ocf.environment.Environment`.
env = ocf.environment.Environment()

# Import our own logging module, which configures logging for us
import ocf.logging  # noqa

# vi:tw=0:wm=0:nowrap:ai:et:ts=8:softtabstop=4:shiftwidth=4
