#!/usr/bin/env python3
# encoding: UTF-8

import argparse
import wave
import sys

__doc__ = """
Reads metadata in WAV files.

"""

def main(args):
    print(args.data)
    return 0

def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    rv.add_argument("data", type=argparse.FileType("r"))
    return rv

def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
