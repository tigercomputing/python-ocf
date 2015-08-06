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

from __future__ import absolute_import

import logging
import ocf
import ocf.syslog
import subprocess
import sys


class HaLogdHandler(logging.Handler):
    """
    Python logger class using ``ha_logger`` to log via ``ha_logd``.
    """
    def emit(self, record):
        """
        Emit a log message given a log record.
        """
        message = self.format(record)

        if record.levelno == logging.DEBUG:
            destination = 'ha-debug'
        else:
            destination = 'ha-log'

        command = [
            'ha_logger',
            '-t', ocf.env.logtag,
            '-D', destination,
            message,
        ]

        subprocess.check_call(command)


def _setup_logging():
    root = logging.getLogger()

    # Simple formatter with just the level name and message
    fmt_short = logging.Formatter("%(levelname)s: %(message)s")

    # Formatter including the logtag
    fmt_long = logging.Formatter("{logtag}: %(levelname)s: %(message)s".format(
        logtag=ocf.env.logtag))

    # Formatter with a very particular format which matches the format used for
    # HA_LOGFILE / HA_DEBUGLOG in ocf-shellfuncs, which includes the date and a
    # tab between the log tag and the date/time.
    fmt_dated = logging.Formatter(
        "{logtag}:\t%(asctime) %(levelname)s: %(message)s".format(
            logtag=ocf.env.logtag),
        datefmt='%Y/%m/%d_%H:%M:%S')

    # Set the log level based on our environment settings
    if ocf.env.debug:
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)

    # If the RA is being run from the command-line, output to stderr only.
    if sys.stdin.isatty():
        # StreamHandler defaults to stderr
        handler = logging.StreamHandler()
        handler.setFormatter(fmt_long)
        root.addHandler(handler)
        return  # all done

    # If the environment asks us to use ha_logd, use that for logging
    # exclusively
    if ocf.env.use_logd:
        handler = HaLogdHandler()
        handler.setFormatter(fmt_short)
        root.addHandler(handler)
        return  # all done

    # Add a syslog handler unless syslog has been explicitly disabled
    if ocf.env.log_facility:
        handler = ocf.syslog.SyslogHandler(
            ident=ocf.env.logtag, facility=ocf.env.log_facility)
        handler.setFormatter(fmt_short)
        root.addHandler(handler)

    # This log file receives _all_ log messages, not just debug logs
    if ocf.env.debuglog:
        handler = logging.FileHandler(ocf.env.debuglog)
        handler.setFormatter(fmt_dated)
        root.addHandler(handler)

    # This log file should not receive DEBUG messages
    if ocf.env.logfile:
        handler = logging.FileHandler(ocf.env.logfile)
        handler.setLevel(logging.INFO)
        handler.setFormatter(fmt_dated)
        root.addHandler(handler)

    # If the root logger has no handlers at this point, add a stderr handler
    if len(root.handlers) == 0:
        # StreamHandler defaults to stderr
        handler = logging.StreamHandler()
        handler.setFormatter(fmt_long)
        root.addHandler(handler)

_setup_logging()

# vi:tw=0:wm=0:nowrap:ai:et:ts=8:softtabstop=4:shiftwidth=4
