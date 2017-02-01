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
            msg = " OK."
        else:
            msg = n
            end = "\n" * clear
        print(msg, end=end, file=sys.stderr, flush=True)

    @staticmethod
    def create(path, start=0, span=None, quiet=False):
        stop = min(100, (start + span) if span is not None else 101)
        Project.progress_point(
            "Creating project tree at {0}".format(path),
            quiet=quiet
        )
        for i in range(start, stop):
            os.makedirs(
                os.path.join(path, "{0:02}".format(i)),
                exist_ok=True,
            )
            Project.progress_point(i, quiet=quiet)
        Project.progress_point(quiet=quiet)
        return len(os.listdir(path))

    @staticmethod
    def refresh(path, start=0, span=None, quiet=False):
        stop = min(100, (start + span) if span is not None else 101)
        Project.progress_point(
            "Refreshing project at {0}".format(path),
            quiet=quiet
        )
        tgts =  sorted(glob.glob(os.path.join(path, "??", "*.wav")))
        for tgt in tgts[start:stop]:
            n = int(os.path.basename(os.path.dirname(tgt)))
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
            Project.progress_point(n, quiet=quiet)

            with open(fP, "w") as new:
                json.dump(history, new, indent=0, sort_keys=True)

            yield history
        Project.progress_point(quiet=quiet)

    @staticmethod
    def vote(path, val=None, incr=0, start=0, span=None, quiet=False):
        tgts = list(Project.refresh(path, start, span, quiet))

        for tgt in tgts:
            tgt["vote"] = val if isinstance(val, int) else tgt["vote"] + incr
            Project.progress_point(
                "{0} vote{1} for slot {2}. Value is {3}".format(
                    "Checked" if not (val or incr) else "Applied",
                    " increment" if val is None and incr else "",
                    os.path.basename(os.path.dirname(tgt["path"])),
                    tgt["vote"]
                ),
                quiet=quiet
            )

            metadata = os.path.join(os.path.dirname(tgt["path"]), "metadata.json")
            with open(metadata, "w") as new:
                json.dump(tgt, new, indent=0, sort_keys=True)

            yield tgt

    @staticmethod
    def check(path, start=0, span=None, quiet=False):
        tgts = list(Project.refresh(path, start, span, quiet=True))
        for tgt in tgts:
            n = int(os.path.basename(os.path.dirname(tgt["path"])))
            if tgt["nchannels"] > 1:
                fP = os.path.splitext(tgt["path"])[0] + ".ref"
                os.replace(tgt["path"], fP)
                with wave.open(fP, "rb") as wav:
                    Audio.wav_to_mono(wav, tgt["path"])

            yield from Project.refresh(path, n, span=1, quiet=True)
            Project.progress_point(n, quiet=quiet)
        Project.progress_point(quiet=quiet)

    def __init__(self,path,  start, span):
        self.path, self.start, self.span = path, start, span
        self._handle = None

    def __enter__(self):
        for metadata in self.check(self.path, self.start, self.span):
            print(metadata)
        # Read data into memory 
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def assemble(self, vote=0):
        print(vote)
