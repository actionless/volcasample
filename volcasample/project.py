#!/usr/bin/env python3
# encoding: UTF-8

from collections import OrderedDict
import glob
import json
import os
import sys
import wave

__doc__ = """
This module provides a workflow for a Volca Sample project.

"""

class Project:

    @staticmethod
    def progress_point(n=None, clear=2):
        if isinstance(n, int):
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
    def create(path, start=0, stop=99):
        Project.progress_point(
            "Creating project tree at {0}".format(path)
        )
        for i in range(start, stop + 1):
            os.makedirs(
                os.path.join(path, "{0:02}".format(i)),
                exist_ok=True,
            )
            Project.progress_point(i)
        Project.progress_point()

    @staticmethod
    def refresh(path):
        Project.progress_point(
            "Refreshing project at {0}".format(path)
        )
        for tgt in glob.glob(os.path.join(path, "??", "*.wav")):
            w = wave.open(tgt, "rb")
            params = w.getparams()
            print(params)
