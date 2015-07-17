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

from __future__ import print_function

import ocf
import os
import sys

from ocf.util import cached_property


class Environment(object):
    """
    Provides interfaces to easily obtain OCF-specific environment information.

    .. note::

       This class should be treated as a singleton and *never* instantiated
       outside the ``ocf`` package. To access properties of this class, an
       instance has been provided as :data:`ocf.env`.

    .. warning::

       When this class is instantiated, it will set the ``LC_ALL`` environment
       variable to ``C`` and unset the ``LANGUAGE`` environment variable.
       Because an instance is created when the ``ocf`` module is imported, any
       script that imports the ``ocf`` module will have these changes applied
       to its environment variables, including any programs executed by the
       script.
    """

    def __init__(self):
        # Try to use a neutral locale (ocf-shellfuncs do this)
        os.environ['LC_ALL'] = 'C'
        try:
            del os.environ['LANGUAGE']
        except KeyError:
            pass

    @cached_property
    def script_name(self):
        """
        The running script's name.

        This may have various different values in Python but we assume that the
        calling script was started using the Python shebang. Returns the
        basename of ``sys.argv[0]``.

        Equivalent to ``$__SCRIPT_NAME`` in shell-based resource agents.
        """
        return os.path.basename(sys.argv[0])

    @cached_property
    def action(self):
        """
        The first command-line argument to the script.

        The OCF-RA-API_ section 3.3 states:

            After the RM has identified the executable to call, the RA will be
            called with the requested action as its sole argument.

            To allow for further extensions, the RA shall ignore all other
            arguments.

        Equivalent to ``$__OCF_ACTION`` in shell-based resource agents.

        .. _OCF-RA-API:
              http://www.opencf.org/cgi-bin/viewcvs.cgi/specs/ra/resource-agent-api.txt?rev=HEAD
        """
        try:
            return sys.argv[1]
        except IndexError:
            return None

    @cached_property
    def ocf_root(self):
        """
        The value of the ``OCF_ROOT`` environment variable.

        If the variable is not defined, a sane default value is used
        (``/usr/lib/ocf``). This variable is the filesystem path to the root of
        the OCF directory hierarchy.
        """
        return os.environ.get('OCF_ROOT', '/usr/lib/ocf')

    @cached_property
    def functions_dir(self):
        """
        The value of the ``OCF_FUNCTIONS_DIR`` environment variable.

        If the variable is not defined, the value is determined by appending
        ``lib/heartbeat`` to :attr:`ocf_root`. This is the directory where the
        resource agents shell function libraries including ``ocf-shellfuncs``
        reside, and is probably of little use within a Python-based resource
        agent script.
        """
        return os.environ.get('OCF_FUNCTIONS_DIR') or \
            os.path.join(self.ocf_root, 'lib/heartbeat')

    @cached_property
    def resource_instance(self):
        """
        The name of the resource instance.

        For primitive (non-clone, non-stateful) resources, this is simply the
        resource name. For clones and stateful resources, this is the primitive
        name, followed by a colon and the clone instance number (such as
        ``p_foobar:0``).
        """
        # If we're being asked for our meta-data, use a generic instance value
        if self.action == 'meta-data':
            return 'undef'

        # Obtain OCF_RESOURCE_INSTANCE from the environment
        ri = os.environ.get('OCF_RESOURCE_INSTANCE')
        if ri is not None:
            return ri

        # We're not being invoked by Pacemaker, so use a reasonable default
        # value for the instance
        if os.environ.get('OCF_RA_VERSION_MAJOR') is None:
            return 'default'

        print('ERROR: Need to tell us our resource instance name.',
              file=sys.stderr)  # FIXME: use HA logging stuff
        sys.exit(ocf.OCF_ERR_ARGS)

    @cached_property
    def resource_type(self):
        """
        The name of the resource type being operated on.

        Obtained from the ``OCF_RESOURCE_TYPE`` environment variable if it is
        present. This is generally equivalent to :attr:`script_name`, which is
        the fallback used if ``OCF_RESOURCE_TYPE`` is not available.
        """
        # Obtain OCF_RESOURCE_TYPE from the environment, or use a sane default
        # value
        return os.environ.get('OCF_RESOURCE_TYPE') or self.script_name

    @cached_property
    def check_level(self):
        # Obtain OCF_CHECK_LEVEL from the environment; may also be known as
        # OCF_RESKEY_OCF_CHECK_LEVEL. If neither is set, use a default value.
        check_level = os.environ.get('OCF_CHECK_LEVEL') or \
            os.environ.get('OCF_RESKEY_OCF_CHECK_LEVEL', 0)
        return int(check_level)

    @property
    def is_root(self):
        """
        Tests whether the agent is running as ``root``.
        """
        return os.getuid() == 0

    @cached_property
    def reskey(self):
        """
        A dictionary of raw agent parameter values.

        This simply filters the environment for all variables whose names start
        ``OCF_RESKEY_``, stripping the prefix from the name. Changes to this
        dictionary are not reflected in ``os.environ[]``.

        Resource agents should use :class:`ocf.ra.Parameter` to define all the
        parameters they expect to receive, however this is a useful accessor
        for CRM-specific parameters such as ``CRM_meta_*`` variables.
        """
        env = os.environ
        return {x[11:]: env[x] for x in env if x.startswith('OCF_RESKEY_')}

    @cached_property
    def is_probe(self):
        """
        Tests whether this is a probe operation.

        Probe operations are run by the CRM when it expects the resource *not*
        to be running, so some of the resource's pre-requisites may not be
        available. Probes are defined as ``monitor`` actions where the
        ``interval`` is zero.

        .. seealso::

           `The OCF Resource Agent Developer's Guide, validate-all action`
             <http://www.linux-ha.org/doc/dev-guides/_literal_validate_all_literal_action.html>
        """
        return self.action == 'monitor' and \
            int(self.reskey.get('CRM_meta_interval', 0)) == 0

    @cached_property
    def is_clone(self):
        """
        Tests whether this resource instance is part of a cloned resource.
        """
        return int(self.reskey.get('CRM_meta_clone_max', 0)) > 0

    @cached_property
    def is_ms(self):
        """
        Tests whether this resource instance is part of a master/slave
        resource.
        """
        return int(self.reskey.get('CRM_meta_master_max', 0)) > 0

# vi:tw=0:wm=0:nowrap:ai:et:ts=8:softtabstop=4:shiftwidth=4
