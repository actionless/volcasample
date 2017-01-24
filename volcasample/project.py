#!/usr/bin/env python3
# encoding: UTF-8

from collections import OrderedDict
import json
import wave

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

def wav_json(metadata, path=None):
    rv = OrderedDict([(k, getattr(metadata, k)) for k in metadata._fields])
    if path is not None:
        rv["path"] = path
        rv.move_to_end("path", last=False)
    return json.dumps(rv, indent=0, sort_keys=False)
