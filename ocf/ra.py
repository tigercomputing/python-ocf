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

import abc
import ocf
import sys

# http://www.opencf.org/cgi-bin/viewcvs.cgi/specs/ra/resource-agent-api.txt?rev=HEAD


class ResourceAgent(object):
    """
    FIXME
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, env):
        self.env = env

    @classmethod
    def main(cls):
        env = ocf.OcfEnvironment()
        agent = cls(env)
        agent.execute()
        sys.exit(ocf.OCF_ERR_GENERIC)  # this should never happen

    def execute(self):
        action_method_name = '{action}_action'.format(
            action=self.env.action.replace('-', '_'))

        action_method = getattr(self, action_method_name)

        action_method()

    @abc.abstractmethod
    def start_action(self):
        pass

    @abc.abstractmethod
    def stop_action(self):
        pass

    @abc.abstractmethod
    def monitor_action(self):
        pass

    def meta_data_action(self):
        # FIXME
        print "META DATA"
        pass

    def validate_all_action(self):
        # FIXME
        print "VALIDATE ALL"
        pass
