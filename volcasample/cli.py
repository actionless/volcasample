#!/usr/bin/env python
#   encoding: UTF-8

# This file is part of volcasample.
#
# volcasample is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# volcasample is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with volcasample.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import os.path
import sys

__doc__ = """
CLI interface to the Volca Sample toolkit.

Operation via CLI requires a set of common options.
Each subcommand may have extra options, like this::

    volcasample <common options> SUBCOMMAND <subcommand options>

"""

DFLT_LOCN = os.path.expanduser(os.path.join("~", "volcasamples"))

def add_common_options(parser):
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    return parser

def add_project_options(parser):
    parser.add_argument(
        "--new", action="store_true", default=False,
        help="Create a new project."
    )
    parser.add_argument(
        "--project", default=DFLT_LOCN,
        help="path to project directory [{}]".format(DFLT_LOCN)
    )
    parser.add_argument(
        "--start", required=False,
        type=int, choices=range(0, 100), default=0,
        help="Select the project index to begin at."
    )
    parser.add_argument(
        "--span", required=False,
        type=int, choices=range(0, 100), default=None,
        help="Select the number of slots to operate on."
    )
    parser.add_argument(
        "--refresh", action="store_true", default=False,
        help="Refresh metadata from audio file(s) in the project."
    )
    parser.add_argument(
        "--preview", action="store_true", default=False,
        help="Play the audio file(s) from the project."
    )
    parser.add_argument(
        "--check", action="store_true", default=False,
        help=(
            "Check the audio file(s) can be loaded to the Volca. "
            "This command coverts stereo files to mono if necessary."
        )
    )
    parser.add_argument(
        "--assemble", action="store_true", default=False,
        help="Create an upload file for the Volca."
        
    )
    parser.add_argument(
        "--vote", required=False, type=str, default=0,
        help=(
            "Change your vote on an audio file. "
            "Use +1, -1 to adjust the vote up or down. "
            "Otherwise supply a digit as the vote value."
        )
    )
    return parser

def add_audio_options(parser):
    parser.add_argument(
        "--delete", action="store_true", default=False,
        help="Delete original audio file after successful conversion."
    )
    parser.add_argument(
        "audio", nargs="*",
        help="Specify one or more audio files."
    )
    return parser

def parser(description=__doc__):
    return argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )

def parsers(description=__doc__):
    rv = parser(description)
    rv = add_common_options(rv)
    subparsers = rv.add_subparsers(
        dest="command",
        help="Commands:",
    )
    p = subparsers.add_parser(
        "project",
        help="Volca Sample 'project' command.",
        description="Operates on your project tree."
    )
    p = add_project_options(p)

    p = subparsers.add_parser(
        "audio",
        help="Volca Sample 'audio' command.",
        description="Operates on audio files."
    )
    p = add_audio_options(p)
    return (rv, subparsers)
