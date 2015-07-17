#!/usr/bin/python

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

import ocf


class TestAgent(ocf.ResourceAgent):
    """
    Python-OCF Test Agent

    The backstore resource manages a Linux-IO (LIO) backing LUN. This LUN
    can then be exported to an initiator via a number of transports,
    including iSCSI, FCoE, Fibre Channel, etc...

    This resource can be run a a single primitive or as a multistate
    (master/slave) resource. When used in multistate mode, the resource
    agent manages ALUA attributes for multipathing.
    """

    # VERSION = '0.0.1'

    hba_type = ocf.Parameter(
        unique=False, required=True, content='string',
        shortdesc='Backing store type', longdesc="""
This attribute is required when running in multistate mode and ignored
otherwise. It is a space separated list of hostnames that this resource might
run on, which is used to generate consistent ALUA port group IDs.
""")

    frobnicate = ocf.Parameter(
        shortdesc="Path to frobnicate binary",
        longdesc="""
            The full path to the frobnicate program. This must be at
            least version 1.0 to work correctly, but version 1.2 or
            above is required to use the superfrobnication
            capabilities.
        """)

    @ocf.Action(timeout=20)
    def start(self):
        print "starting"

    @ocf.Action(timeout=20)
    def stop(self):
        print "stopping"

    @ocf.Action(timeout=20, depth=0, interval=10)
    @ocf.Action(timeout=20, depth=0, interval=20, role="Slave")
    @ocf.Action(timeout=20, depth=0, interval=10, role="Master")
    def monitor(self):
        print "monitoring"
        print "hba_type: " + self.hba_type

if __name__ == "__main__":
    TestAgent.main()

# vi:tw=0:wm=0:nowrap:ai:et:ts=8:softtabstop=4:shiftwidth=4
