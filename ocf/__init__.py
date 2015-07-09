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

from ocf.version import __version__  # noqa


# Constants for resource script exit values
OCF_SUCCESS = 0
OCF_ERR_GENERIC = 1
OCF_ERR_ARGS = 2
OCF_ERR_UNIMPLEMENTED = 3
OCF_ERR_PERM = 4
OCF_ERR_INSTALLED = 5
OCF_ERR_CONFIGURED = 6
OCF_NOT_RUNNING = 7

# Non-standard values.
#
# OCF does not include the concept of master/slave resources so we
#   need to extend it so we can discover a resource's complete state.
#
# OCF_RUNNING_MASTER:
#    The resource is in "master" mode and fully operational
# OCF_FAILED_MASTER:
#    The resource is in "master" mode but in a failed state
#
# The extra two values should only be used during a probe.
#
# Probes are used to discover resources that were started outside of
#    the CRM and/or left behind if the LRM fails.
#
# They can be identified in RA scripts by checking for:
#  [ "${__OCF_ACTION}" = "monitor" -a "${OCF_RESKEY_CRM_meta_interval}" = "0" ]
#
# Failed "slaves" should continue to use: OCF_ERR_GENERIC
# Fully operational "slaves" should continue to use: OCF_SUCCESS
#
OCF_RUNNING_MASTER = 8
OCF_FAILED_MASTER = 9

# Import these at the end so that the circular references don't go haywire
from ocf.env import OcfEnvironment  # noqa
from ocf.ra import ResourceAgent  # noqa
