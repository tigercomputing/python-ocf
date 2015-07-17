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

import inspect
import ocf
import sys

from lxml import etree
from ocf.util import cached_property


class ResourceAgentType(type):
    """
    Metaclass that adds special behaviour to :class:`ResourceAgent` classes.

    In particular, this handles collecting metadata about actions and
    parameters as defined using :class:`Action` and :class:`Parameter`.

    This should not be used outside of the :class:`ResourceAgent` class.
    """
    def __new__(cls, name, bases, attrs):
        # Create the class with only the __module__ attribute set; other
        # attributes will be added back in later
        module = attrs.pop('__module__')
        new_class = super(ResourceAgentType, cls).__new__(
            cls, name, bases, {'__module__': module})

        # Copy the actions and parameters from the parent class, if any. These
        # can be overridden by child classes if required.
        try:
            new_class.add_to_class('_ACTIONS', bases[0]._ACTIONS)
        except AttributeError:
            new_class.add_to_class('_ACTIONS', {})

        try:
            new_class.add_to_class('_PARAMETERS', bases[0]._PARAMETERS)
        except AttributeError:
            new_class.add_to_class('_PARAMETERS', {})

        # Re-add all other attributes to the class, optinally using
        # contribute_to_class() if it's defined
        for name, value in attrs.items():
            new_class.add_to_class(name, value)

        return new_class

    def add_to_class(cls, name, value):
        """
        Helper to used to copy attributes into the resource agent class.

        This method is called once for every attribute of declared classes that
        use this metaclass, and their sub-classes. If the attribute is `not` a
        class and has a :meth:`contribute_to_class` method, this method is
        called so that the object in the attribute may become aware of the
        resource agent in which it has been declared. If it doesn't,
        :func:`setattr` is called so that the attribute is copied unchanged.

        :meth:`contribute_to_class` should be defined as:

        .. py:method:: contribute_to_class(self, ra, name)
        """
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and \
                hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Parameter(object):
    """
    Defines a parameter used by a resource agent.

    This class is used by :class:`ResourceAgent` sub-classes in order to
    document the parameters that the resource agent expects. The values given
    to the constructor are used to construct the XML metadata returned to the
    CRM in response to a ``meta-data`` query.

    :param str shortdesc: One-line description of this parameter. Required.
    :param str longdesc: Multi-line long description of this parameter.
      Required.
    :param bool unique: Whether the value should be unique across *all*
      instances of this resource agent.
    :param bool required: Whether a value is required to be given in the
      configuration.
    :param str content: Expected type of the value. Can be one of ``string``,
      ``integer`` or ``boolean``.
    :param str default: For non-``required`` resources, a default value to use
      if the parameter is not specified in the configuration.

    Usage::

        class MyAgent(ocf.ResourceAgent):
            frobnicate = ocf.Parameter(
                shortdesc="Path to frobnicate binary",
                longdesc=\"\"\"
                    The full path to the frobnicate program. This must be at
                    least version 1.0 to work correctly, but version 1.2 or
                    above is required to use the superfrobnication
                    capabilities.
                \"\"\")
            ...

    This generates XML metadata of the form:

    .. code-block:: xml

        <parameter name="frobnicate" unique="0">
          <longdesc lang="en">
                The full path to the frobnicate program. This must be at
                least version 1.0 to work correctly, but version 1.2 or
                above is required to use the superfrobnication
                capabilities.
            </longdesc>
          <shortdesc lang="en">Path to frobnicate binary</shortdesc>
          <content type="string"/>
        </parameter>

    The value of the parameter may be obtained within the resource agent class
    using a simple variable access::

        print("path to frobnicate: ", self.frobnicate)

    .. note::

        This class is a data descriptor.
    """
    def __init__(self, shortdesc, longdesc, unique=False, required=False,
                 content='string', default=None):
        self.shortdesc = shortdesc
        self.longdesc = longdesc
        self.unique = unique
        self.required = required
        self.content = content
        self.default = default
        self.__doc__ = shortdesc

        if content not in ['string', 'integer', 'boolean']:
            raise ValueError('content must be one of string, integer or '
                             'boolean')

        if default is not None:
            if required:
                raise ValueError('parameter cannot both be required and have '
                                 'a default value')
            else:
                self._validate_coerce(self, default)

    def contribute_to_class(self, ra, name):
        """
        Called by :meth:`ResourceAgentType.add_to_class` so that this instance
        can influence how it appears in the resulting :class:`ResourceAgent`
        sub-class.

        Specifically, this remembers the variable name from the assignment and
        adds itself to the internal :data:`ResourceAgent._PARAMETERS`
        dictionary.
        """
        ra._PARAMETERS[name] = self
        self.name = name
        setattr(ra, name, self)

    def append_xml(self, parameters):
        """
        Called by :meth:`ResourceAgent.meta_data` in order to construct the XML
        metadata structure for this parameter.
        """
        p = etree.SubElement(
            parameters, 'parameter', name=self.name,
            unique='1' if self.unique else '0')

        if self.required:
            p.set('required', '1')

        etree.SubElement(p, 'longdesc', lang='en').text = self.longdesc
        etree.SubElement(p, 'shortdesc', lang='en').text = self.shortdesc

        c = etree.SubElement(p, 'content', type=self.content)
        if self.default is not None and not self.required:
            c.set('default', self.default)

    def _validate_coerce(self, value):
        if self.content == 'string':
            return str(value)
        elif self.content == 'integer':
            return int(value)
        elif self.content == 'boolean':
            # The list of "true" values comes from ocf-shellfuncs:ocf_is_true
            return str(value) in ['yes', 'true', '1', 'YES', 'TRUE', 'ya',
                                  'on', 'ON']
        else:
            raise NotImplementedError("Unknown parameter type: {t}".format(
                                      t=self.content))

    @cached_property
    def _value(self):
        try:
            value = ocf.env.reskey[self.name]
        except KeyError:
            if self.required:
                raise ValueError("Required parameter {p} not set".format(
                                 p=self.name))
            else:
                return self.default
        else:
            return self._validate_coerce(value)

    def validate(self):
        """
        Validates the property against the value in the environment.

        This is called internally by
        :meth:`ResourceAgent._validate_parameters`.

        :raises ValueError: if the parameter is required but not set in the
          environment or if the value is of the wrong type.
        """
        # Simply try to obtain our value, the property getter takes care of
        # validation
        self._value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self._value

    def __set__(self, instance, value):
        raise AttributeError("parameter '{name}' is not settable".format(
            name=self.name))


class Action(object):
    """
    Defines an action that a resource agent can be asked to perform.

    This class is a decorator used by :class:`ResourceAgent` sub-classes in
    order to document available resource agent actions. The values given to the
    constructor are used to construct the XML metadata returned to the CRM in
    response to a ``meta-data`` query. The same function may be decorated
    multiple times with this decorator: this is particularly useful for the
    ``monitor`` action which may have several different modes of operation,
    such as different ``depth`` or ``role`` values.

    :param str name: Name of this action (see
      :data:`ocf.environment.Environment.action`). Optional; uses the decorated
      function's name if not specified.
    :param int timeout: Recommended minimum timeout for this action in seconds.
      This is enforced by the CRM. Optional.
    :param int interval: Recommended minimum interval between calls to this
      action. Only relevant for recurring actions such as ``monitor``.
      Optional.
    :param int start_delay: Recommended minimum start delay for this action.
      Optional.
    :param int depth: For ``monitor`` operations only: a measure of how
      thorough the check should be. See below. Optional.
    :param str role: For ``monitor`` operations on resource agents that can
      support master/slave operation only. Optional.

    Usage::

        class MyAgent(ocf.ResourceAgent):
            @ocf.Action(timeout=40)
            def start(self):
                ...
            @ocf.Action(timeout=20, depth=0, interval=10)
            @ocf.Action(timeout=20, depth=0, interval=20, role="Slave")
            @ocf.Action(timeout=20, depth=0, interval=10, role="Master")
            def monitor(self):
                ...

    This generates XML metadata of the form:

    .. code-block:: xml

        <action name="monitor" timeout="20" interval="10" depth="0"/>
        <action name="monitor" timeout="20" interval="20" depth="0"
            role="Slave"/>
        <action name="monitor" timeout="20" interval="10" depth="0"
            role="Master"/>
        <action name="start" timeout="40"/>
    """
    def __init__(self, name=None, timeout=20, interval=None, start_delay=None,
                 depth=None, role=None):
        self.name = name
        self.timeout = timeout
        self.interval = interval
        self.start_delay = start_delay
        self.depth = depth
        self.role = role

    @property
    def action_method(self):
        """
        Returns the wrapped method/function.

        Used by :meth:`ResourceAgent.execute` to run the chosen action, even if
        it has been decorated multiple times (this ends up chaining several
        instances of this class, internally).
        """
        if isinstance(self.action, Action):
            return self.action.action_method
        else:
            return self.action

    def __call__(self, action):
        self.action = action

        if isinstance(action, Action):
            if self.name is None:
                self.name = action.name
            assert self.name == action.name
        else:
            if self.name is None:
                self.name = action.__name__

        return self

    def contribute_to_class(self, ra, name):
        """
        Called by :meth:`ResourceAgentType.add_to_class` so that this instance
        can influence how it appears in the resulting :class:`ResourceAgent`
        sub-class.

        Specifically, this adds itself to the internal
        :data:`ResourceAgent._ACTIONS` dictionary, and ends up setting the
        unwrapped function in the class so that the resource agent (any any
        sub-classes) need not play games to call actions internally.
        """
        ra._ACTIONS[self.name] = self
        setattr(ra, name, self.action_method)

    def append_xml(self, actions):
        """
        Called by :meth:`ResourceAgent.meta_data` in order to construct the XML
        metadata structure for this action.
        """
        a = etree.SubElement(
            actions, 'action', name=self.name, timeout=str(self.timeout))

        if self.interval is not None:
            a.set('interval', str(self.interval))

        if self.start_delay is not None:
            a.set('start-delay', str(self.start_delay))

        if self.depth is not None:
            a.set('depth', str(self.depth))

        if self.role is not None:
            a.set('role', str(self.role))

        if isinstance(self.action, Action):
            self.action.append_xml(actions)


class ResourceAgent(object):
    """
    FIXME
    """
    __metaclass__ = ResourceAgentType

    @classmethod
    def main(cls):
        cls().execute()
        sys.exit(ocf.OCF_ERR_GENERIC)  # this should never happen

    def __init__(self):
        super(ResourceAgent, self).__init__()

        required_actions = frozenset(['start', 'stop', 'monitor', 'meta-data'])
        missing_actions = required_actions - frozenset(self._ACTIONS)
        if missing_actions:
            raise NotImplementedError(
                ("{cls} is incomplete; it is missing the following required "
                 "actions: {act}").format(
                     cls=self.__class__,
                     act=", ".join(sorted(missing_actions))))

    def execute(self):
        # If we were called without any arguments, print usage and exit
        if ocf.env.action is None:
            self._print_usage()
            sys.exit(ocf.OCF_ERR_ARGS)

        # Lookup the action method by name. If there is no such method, print
        # usage and exit with OCF_ERR_UNIMPLEMENTED
        try:
            action = self._ACTIONS[ocf.env.action]
        except KeyError:
            print("{action}: action not supported".format(
                action=ocf.env.action), file=sys.stderr)  # FIXME: use HA log
            self._print_usage()
            sys.exit(ocf.OCF_ERR_UNIMPLEMENTED)

        # Handle "simple" actions here right away as a short-cut, bypassing the
        # various pre-requisite checks
        if ocf.env.action in ['meta-data']:
            action.action_method(self)
            sys.exit(ocf.OCF_SUCCESS)  # this should never happen

        # Validate all required parameters have been given
        self._validate_parameters()

        # Run the requested action
        action.action_method(self)

        sys.exit(ocf.OCF_ERR_GENERIC)  # this should never happen

    def _print_usage(self):
        print("Usage: {env.script_name} {{{actions}}}".format(
            env=ocf.env, actions="|".join(sorted(self._ACTIONS))),
            file=sys.stderr)

    def _validate_parameters(self):
        for p in self._PARAMETERS.itervalues():
            try:
                p.validate()
            except ValueError as e:
                # FIXME: use HA logging
                print("ERROR: {e.message}".format(e=e), file=sys.stderr)
                sys.exit(ocf.OCF_ERR_CONFIGURED)

    @Action(name='meta-data', timeout=5)
    def meta_data(self):
        try:
            name = self.NAME
        except AttributeError:
            name = ocf.env.script_name

        xra = etree.Element('resource-agent', name=name)

        # Add the optional version number if we have one
        try:
            xra.set('version', self.VERSION)
        except AttributeError:
            pass

        # API version number; currently 1.0
        etree.SubElement(xra, 'version').text = '1.0'

        # We extract the RA's short and long description from the docstring on
        # the ResourceAgent subclass.
        doc_lines = self.__class__.__doc__.strip().split("\n")

        # The short description is the first line of the docstring
        shortdesc = doc_lines.pop(0)

        # The long description is everything that's left
        longdesc = "\n".join(x.strip() for x in doc_lines) + "\n"

        # Add in the RA description text. We just assume the language will
        # always only be English; to date the author has not seen anything but
        # in a published resource agent script.
        etree.SubElement(xra, 'longdesc', lang='en').text = longdesc
        etree.SubElement(xra, 'shortdesc', lang='en').text = shortdesc

        parameters = etree.SubElement(xra, 'parameters')
        for param in self._PARAMETERS.itervalues():
            param.append_xml(parameters)

        actions = etree.SubElement(xra, 'actions')
        for action in self._ACTIONS.itervalues():
            action.append_xml(actions)

        print(etree.tostring(
            xra, pretty_print=True, xml_declaration=True, encoding='utf-8',
            doctype='<!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">'))

    @Action(name='validate-all', timeout=5)
    def validate_all(self):
        # Parameters are validated by _validate_parameters(); we have nothing
        # further to do here. Subclasses may override this method (or the whole
        # action if necessary) to do their own additional checks if required.
        sys.exit(ocf.OCF_SUCCESS)

# vi:tw=0:wm=0:nowrap:ai:et:ts=8:softtabstop=4:shiftwidth=4
