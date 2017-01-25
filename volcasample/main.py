#!/usr/bin/env python3
# encoding: UTF-8

import argparse
from collections import OrderedDict
import json
import glob
import os.path
import sys
import wave

import volcasample
import volcasample.cli
import volcasample.project

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

def main(args):
    if args.command == "sample":
        for path in args.samples:
            w = wave.open(path, "rb")
            metadata = w.getparams()
            print(volcasample.project.wav_json(metadata, path=os.path.abspath(path)))
    elif args.command == "project":
        if args.new:
            volcasample.project.Project.create(
                args.project,
                start=args.start,
                stop=args.stop or 99
            )
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
