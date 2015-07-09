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

# ocf-binaries ###

# Make sure PATH contains all the usual suspects
# PATH="$PATH:/sbin:/bin:/usr/sbin:/usr/bin"

# check_binary () {
#     if ! have_binary "$1"; then
#     if [ "$OCF_NOT_RUNNING" = 7 ]; then
#         # Chances are we have a fully setup OCF environment
#         ocf_log err "Setup problem: couldn't find command: $1"
#     else
#         echo "Setup problem: couldn't find command: $1"
#     fi
#     exit $OCF_ERR_INSTALLED
#     fi
# }

# have_binary () {
#     if [ "$OCF_TESTER_FAIL_HAVE_BINARY" = "1" ]; then
#         false
#     else
#     local bin=`echo $1 | sed -e 's/ -.*//'`
#     test -x "`which $bin 2>/dev/null`"
#     fi
# }
