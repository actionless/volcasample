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

import bisect
from collections import OrderedDict
from collections import namedtuple
import functools
import glob
import json
import os
import sys
import wave

from volcasample.audio import Audio
import volcasample.syro

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

class Project:

    plot = functools.partial(
        print, sep="", end="", file=sys.stdout, flush=True
    )

    @staticmethod
    def scale(pos=0, n=100):
        Project.plot(*[i // 10 for i in range(pos, n)])
        Project.plot("\n")
        Project.plot(*[i % 10 for i in range(pos, n)])
        Project.plot("\n")

    @staticmethod
    def progress_point(n=None, clear=2, quiet=False, file_=sys.stderr):
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
            end = "" if len(n) == 1 else "\n" * clear
        print(msg, end=end, file=file_, flush=True)

    @staticmethod
    def parse_initial(text):
        return OrderedDict([
            (int(f + s), {" ": None, "x": False}.get(t.lower(), True))
            for f, s, t in zip(*text.splitlines())
        ])
        
    @staticmethod
    def optimise(targets, initial:list, vote):
        jobs = OrderedDict([(
            tgt["slot"],
            (volcasample.syro.DataType.Sample_Erase, tgt["path"]))
            for tgt, keep in zip(targets, initial)
            if "path" in tgt and keep is False
        ])
        jobs.update(OrderedDict([(
            tgt["slot"],
            (volcasample.syro.DataType.Sample_Compress, tgt["path"]))
            for tgt, keep in zip(targets, initial)
            if "path" in tgt and keep is True
        ]))
        return jobs

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
        tgts = (
            os.path.join(path, "{0:02}".format(i), "*.wav")
            for i in range(start, stop)
        )
        for n, tgt in zip(range(start, stop), tgts):
            # Metadata defaults
            metadata = OrderedDict([("slot", n), ("vote", 0)])

            # Try to load previous metadata
            fP = os.path.join(
                path, "{0:02}".format(n), "metadata.json"
            )
            try:
                with open(fP, "r") as prev:
                    metadata.update(json.load(prev))
            except FileNotFoundError:
                pass  # Use default values for metadata

            try:
                src = next(iter(glob.glob(tgt)))
                w = wave.open(src, "rb")
                params = w.getparams()
                metadata.update(Audio.metadata(params, src))
            except (FileNotFoundError, StopIteration):
                pass  # Use default values for metadata

            Project.progress_point(n, quiet=quiet)

            with open(fP, "w") as new:
                json.dump(metadata, new, indent=0, sort_keys=True)

            yield metadata
        Project.progress_point(quiet=quiet)

    @staticmethod
    def vote(path, val=None, incr=0, start=0, span=None, quiet=False):
        stop = min(100, (start + span) if span is not None else 101)
        tgts = list(Project.refresh(path, start, span, quiet))

        for n, tgt in zip(range(start, stop), tgts):
            tgt["vote"] = val if isinstance(val, int) else tgt["vote"] + incr
            Project.progress_point(
                "{0} vote{1} for slot {2:02}. Value is {3}".format(
                    "Checked" if not (val or incr) else "Applied",
                    " increment" if val is None and incr else "",
                    n, tgt.get("vote", 0)
                ),
                quiet=quiet
            )

            metadata = os.path.join(path, "{0:02}".format(n), "metadata.json")
            with open(metadata, "w") as new:
                json.dump(tgt, new, indent=0, sort_keys=True)

            yield tgt

    @staticmethod
    def check(path, start=0, span=None, quiet=False):
        stop = min(100, (start + span) if span is not None else 101)
        tgts = list(Project.refresh(path, start, span, quiet=True))
        for n, tgt in zip(range(start, stop), tgts):
            if tgt.get("nchannels", 0) > 1 or tgt.get("sampwidth", 0) > 2:
                fP = os.path.splitext(tgt["path"])[0] + ".ref"
                try:
                    os.replace(tgt["path"], fP)
                    with wave.open(fP, "rb") as wav:
                        Audio.wav_to_mono(wav, tgt["path"])
                except FileNotFoundError:
                    pass

            yield from Project.refresh(path, n, span=1, quiet=True)
            Project.progress_point(n, quiet=quiet)
        Project.progress_point(quiet=quiet)

    def audition(path, start=0, span=None, quiet=False, silent=False):

        def grade(
            nFrames,
            breaks=[1, 20 * 1024, 100 * 1024, 500 * 1024, 2 * 1024 * 1024],
            ramp=" .:iI#"
        ):
            return ramp[bisect.bisect(breaks, nFrames)]

        stop = min(100, (start + span) if span is not None else 101)
        Project.progress_point(
            "Auditioning project at {0}".format(path),
            quiet=quiet
        )
        tgts = list(Project.refresh(path, start, span, quiet=True))

        Project.scale(start, stop)
        # 4 MB, 65s
       
        
        grades = [grade(tgt.get("nframes", 0)) for tgt in tgts]
        
        for n, grd, tgt in zip(range(start, stop), grades, tgts):
            if "path" in tgt:
                Project.plot(grd)
                wav = wave.open(tgt["path"], "rb")
                if not silent:
                    rv = Audio.play(wav)
                    if rv is None:
                        return
                    else:
                        rv.wait_done()
                yield wav
            else:
                Project.plot(" ")
                yield None
        Project.progress_point(quiet=quiet)

    def __init__(self,path, start, span, quiet=True):
        self.path, self.start, self.span = path, start, span
        self.quiet = quiet
        self._assets = []

    def __enter__(self):
        self._assets = []
        for metadata in self.check(
            self.path, self.start, self.span, quiet=self.quiet
        ):
            self._assets.append(metadata)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._assets = []
        return False

    def assemble(self, locn, initial=[], vote=0, optimiser=None):
        optimiser = optimiser or Project.optimise
        jobs = optimiser(self._assets, initial, vote)

        if jobs:
            patch = volcasample.syro.SamplePacker.patch(jobs)
            status = volcasample.syro.SamplePacker.build(patch, locn)
            return status
