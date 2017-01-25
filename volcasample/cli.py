#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

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
        "--new", action="store_true", required=False,
        help="Create a new project."
    )
    parser.add_argument(
        "--project", default=DFLT_LOCN,
        help="path to project directory [{}]".format(DFLT_LOCN))
    parser.add_argument(
        "--start", required=False,
        type=int, choices=range(0, 100), default=0,
        help="Select the project index to begin at."
    )
    parser.add_argument(
        "--stop", required=False,
        type=int, choices=range(0, 100), default=0,
        help="Select the project index to end on."
    )
    parser.add_argument(
        "--preview", action="store_true", default=False,
        help="Play the sample file(s) from the project."
    )
    parser.add_argument(
        "--vote", required=False, type=str,
        help=(
            "Change your vote on a sample. "
            "Use +1, -1 to adjust the vote up or down. "
            "Otherwise supply a digit as the vote value."
        )
    )
    return parser

def add_sample_options(parser):
    parser.add_argument(
        "--delete", action="store_true", default=False,
        help="Delete original sample file after successful conversion."
    )
    parser.add_argument(
        "samples", nargs="*",
        help="Specify one or more sample files."
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
        "sample",
        help="Volca Sample 'sample' command.",
        description="Operates on sample files."
    )
    p = add_sample_options(p)
    return (rv, subparsers)
