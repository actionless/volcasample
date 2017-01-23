#!/usr/bin/env python3
# encoding: UTF-8

import argparse
import cmd
from collections import OrderedDict
import json
import glob
import os.path
import sys

__doc__ = """
Manages sets of samples for encoding to device.

"""

def main(args):
    return 0

def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    rv.add_argument(
        "--project",
        help="Specify the path to the root of a project"
    )
    return rv

def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
