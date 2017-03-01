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

import os.path
import shutil
import tempfile
import textwrap
import unittest

import pkg_resources

from volcasample.project import Project
from volcasample.syro import Status


class NeedsTempDirectory:

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

class CopiesTestData(NeedsTempDirectory):

    def setUp(self):
        super().setUp()
        self.assertEqual(
            3,
            Project.create(self.drcty.name, start=0, span=3, quiet=True)
        )
        data = pkg_resources.resource_filename("volcasample.test", "data")
        for src, dst in zip(
            sorted(i for i in os.listdir(data) if i.endswith(".wav")),
            ("00", "01", "02")
        ):
            rv = shutil.copy(os.path.join(data, src), os.path.join(self.drcty.name, dst))

class ProjectCreateTests(NeedsTempDirectory, unittest.TestCase):

    def test_all_subdirectories(self):
        rv = Project.create(self.drcty.name, quiet=True)
        self.assertEqual(100, rv)
        self.assertEqual(
            {"{0:02}".format(i) for i in range(100)},
            set(os.listdir(self.drcty.name))
        )

    def test_select_subdirectories(self):
        for start, span in zip(range(49, -1, -1), range(1, 100)):
            with self.subTest(start=start, span=span):
                rv = Project.create(self.drcty.name, start=start, span=span, quiet=True)
                self.assertEqual(span, rv)
                self.assertEqual(
                    {"{0:02}".format(i) for i in range(start, start + span)},
                    set(os.listdir(self.drcty.name))
                )

class ProjectRefreshTests(CopiesTestData, unittest.TestCase):

    def test_refresh_no_history(self):
        rv = list(Project.refresh(self.drcty.name, start=0, span=3, quiet=True))
        for metadata in rv:
            self.assertTrue(all(i in metadata for i in (
                "path", "vote", "nchannels", "sampwidth"
            )))
            self.assertEqual(0, metadata["vote"])
            self.assertTrue(os.path.isfile(metadata["path"]))

    def test_select_refresh_no_history(self):
        rv = list(Project.refresh(self.drcty.name, start=0, span=1, quiet=True))
        self.assertEqual(1, len(rv))
        metadata = rv[0]
        self.assertTrue(all(i in metadata for i in (
            "path", "vote", "nchannels", "sampwidth"
        )))
        self.assertEqual(0, metadata["vote"])
        self.assertTrue(os.path.isfile(metadata["path"]))

    def test_refresh_with_history(self):
        with open(os.path.join(self.drcty.name, "00", "metadata.json"), "w") as history:
            history.write('{"vote": 16472}')
        rv = next(Project.refresh(self.drcty.name, quiet=True))
        self.assertEqual(16472, rv["vote"])

class ProjectVoteTests(CopiesTestData, unittest.TestCase):

    def test_vote_single_value(self):
        rv = next(Project.vote(self.drcty.name, val=16472, start=0, span=1, quiet=True))
        self.assertEqual(16472, rv["vote"])

    def test_vote_many_value(self):
        rv = list(Project.vote(self.drcty.name, val=16472, start=0, span=2, quiet=True))
        self.assertTrue(all(i["vote"] == 16472 for i in rv))
        self.assertEqual(2, len(rv))

    def test_vote_single_positive_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=1, quiet=True))
        rv = next(Project.vote(self.drcty.name, incr=2, start=0, span=1, quiet=True))
        self.assertEqual(16474, rv["vote"])

    def test_vote_single_negative_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=1, quiet=True))
        rv = next(Project.vote(self.drcty.name, incr=-2, start=0, span=1, quiet=True))
        self.assertEqual(16470, rv["vote"])

    def test_vote_many_positive_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=2, quiet=True))
        rv = list(Project.vote(self.drcty.name, incr=2, start=0, span=2, quiet=True))
        self.assertTrue(all(i["vote"] == 16474 for i in rv))
        self.assertEqual(2, len(rv))

    def test_vote_many_negative_increment(self):
        list(Project.vote(self.drcty.name, val=16472, start=0, span=2, quiet=True))
        rv = list(Project.vote(self.drcty.name, incr=-2, start=0, span=2, quiet=True))
        self.assertTrue(all(i["vote"] == 16470 for i in rv))
        self.assertEqual(2, len(rv))

class ProjectCheckTests(CopiesTestData, unittest.TestCase):

    def test_check_single_slot(self):
        rv = next(Project.check(self.drcty.name, start=0, span=1, quiet=True))
        self.assertEqual(1, rv["nchannels"])
        self.assertTrue(os.path.isfile(os.path.join(os.path.splitext(rv["path"])[0] + ".ref")))

class ProjectAssembleTests(CopiesTestData, unittest.TestCase):

    def test_parse_instructions(self):
        text = textwrap.dedent("""
        00000000001111111111
        01234567890123456789
        ..X~...      XXXXXXX
        """
        ).lstrip()
        initial = Project.parse_initial(text)
        targets = list(Project.refresh(
            self.drcty.name, start=0, span=3, quiet=True
        ))
        jobs = Project.optimise(targets, initial.values(), 0)
        self.assertEqual([2, 0, 1], list(jobs.keys()))

    def test_assemble_single_slot(self):
        with Project(self.drcty.name, 0, 1) as proj:
            status, fP = proj.assemble(initial=[True], locn=self.drcty.name)
        self.assertIs(status, Status.Success)

    def test_assemble_three_slots(self):
        with Project(self.drcty.name, 0, 3, quiet=True) as proj:
            status, fP = proj.assemble(initial=[True] * 3, locn=self.drcty.name)
        self.assertIs(status, Status.Success)
