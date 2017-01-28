#!/usr/bin/env python3
# encoding: UTF-8

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
import volcasample.project
from volcasample.audio import Audio

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

def main(args):
    if args.command == "audio":
        for path in args.samples:
            w = wave.open(path, "rb")
            params = w.getparams()
            print(Audio.metadata(params, path=os.path.abspath(path)))
    elif args.command == "project":
        if args.new:
            volcasample.project.Project.create(
                args.project,
                start=args.start,
                span=args.span
            )
        elif args.refresh:
            list(volcasample.project.Project.refresh(
                args.project,
                start=args.start,
                span=args.span
            ))
        elif args.vote:
            try:
                val = int(args.vote)
            except ValueError:
                stats = Counter(
                    i["vote"] for i in volcasample.project.Project.vote(
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
                    list(volcasample.project.Project.vote(
                        args.project,
                        incr=val,
                        start=args.start,
                        span=args.span
                    ))
                else:
                    list(volcasample.project.Project.vote(
                        args.project,
                        val=val,
                        start=args.start,
                        span=args.span
                    ))
        elif args.check:
            list(volcasample.project.Project.check(
                args.project,
                start=args.start,
                span=args.span
            ))
    return 0

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
