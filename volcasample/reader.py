#!/usr/bin/env python3
# encoding: UTF-8

import argparse
from collections import OrderedDict
import json
import glob
import os.path
import sys
import wave

__doc__ = """
Reads metadata in WAV files.

"""

def wav_json(metadata, path=None):
    rv = OrderedDict([(k, getattr(metadata, k)) for k in metadata._fields])
    if path is not None:
        rv["path"] = path
        rv.move_to_end("path", last=False)
    return json.dumps(rv, indent=0, sort_keys=False)

def main(args):
    for path in glob.glob(os.path.expanduser(args.pattern)):
        w = wave.open(path, "rb")
        metadata = w.getparams()
        print(wav_json(metadata, path=os.path.abspath(path)))
    return 0

def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    rv.add_argument("pattern", help="Set a glob path to identify WAV files")
    return rv

def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
