#!/usr/bin/env python3
# encoding: UTF-8

from collections import OrderedDict
import glob
import json
import os
import sys
import wave

from volcasample.audio import Audio

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

class Project:

    @staticmethod
    def progress_point(n=None, clear=2, quiet=False):
        if quiet:
            return
        elif isinstance(n, int):
            msg = "." if n % 10 else n // 10
            end = ""
        elif n is None:
            end = "\n" * clear
            msg = " Done."
        else:
            msg = n
            end = "\n" * clear
        print(msg, end=end, file=sys.stderr, flush=True)

    @staticmethod
    def create(path, start=0, stop=99, quiet=False):
        Project.progress_point(
            "Creating project tree at {0}".format(path),
            quiet=quiet
        )
        for i in range(start, stop + 1):
            os.makedirs(
                os.path.join(path, "{0:02}".format(i)),
                exist_ok=True,
            )
            Project.progress_point(i, quiet=quiet)
        Project.progress_point(quiet=quiet)
        return len(os.listdir(path))

    @staticmethod
    def refresh(path, quiet=False):
        Project.progress_point(
            "Refreshing project at {0}".format(path),
            quiet=quiet
        )
        for tgt in glob.glob(os.path.join(path, "??", "*.wav")):
            w = wave.open(tgt, "rb")
            params = w.getparams()
            metadata = Audio.metadata(params, tgt)

            # Try to load previous metadata
            slot = os.path.dirname(tgt)
            fP = os.path.join(slot, "metadata.json")

            try:
                with open(fP, "r") as prev:
                    history = json.load(prev)
            except FileNotFoundError:
                history = OrderedDict([("vote", 0)])

            history.update(metadata)
            Project.progress_point(history, quiet=quiet)

            with open(fP, "w") as new:
                json.dump(history, new, indent=0)

            yield history
