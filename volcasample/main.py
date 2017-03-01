#!/usr/bin/env python3
# encoding: UTF-8

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
from collections import Counter
from collections import OrderedDict
import json
import glob
import os.path
import sys
import wave

import volcasample
import volcasample.cli
from volcasample.audio import Audio
from volcasample.project import Project
from volcasample.syro import Status

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

def main(args):
    rv = 0
    if args.command == "audition":
        list(Project.audition(
            args.project,
            start=args.start,
            span=args.span,
            silent=args.silent
        ))
    elif args.command == "patch":
        initial = Project.parse_initial(args.instructions.read())
        with Project(args.project, args.start, args.span) as proj:
            status, fP = proj.assemble(args.project, initial=initial.values())
            print(status, file=sys.stderr)
            if status is Status.Success and not args.silent:
                with wave.open(fP, "rb") as wav:
                    audio = Audio.play(wav)
                    if audio is None:
                       rv = 1 
                    else:
                        audio.wait_done()

    elif args.command == "project":

        if args.new:
            Project.create(
                args.project,
                start=args.start,
                span=args.span
            )
        elif args.vote:
            try:
                val = int(args.vote)
            except ValueError:
                stats = Counter(
                    i["vote"] for i in Project.vote(
                        args.project,
                        start=args.start,
                        span=args.span,
                        quiet=True
                    )
                )
                print("Vote value    Total", file=sys.stderr)
                print(
                    *["{0: 10}     {1:02}".format(val, stats[val]) for val in sorted(stats.keys())],
                    file=sys.stdout
                )
            else:
                if args.vote[0] in "+-":
                    list(Project.vote(
                        args.project,
                        incr=val,
                        start=args.start,
                        span=args.span
                    ))
                else:
                    list(Project.vote(
                        args.project,
                        val=val,
                        start=args.start,
                        span=args.span
                    ))
        elif args.check:
            list(Project.check(
                args.project,
                start=args.start,
                span=args.span,
            ))
    return rv

def run():
    p, subs = volcasample.cli.parsers()
    args = p.parse_args()
    rv = 0
    if args.version:
        sys.stdout.write(volcasample.__version__ + "\n")
    else:
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
