"""
Point to the middle of the object/padding
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestMiddlePointer(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_middle_pointer(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        self.expect("vp", substrs=['"pa1" points to object "foo.a"',
                                   '"pa2" points to object "foo.a (offset +1)"',
                                   '"pb1" points to object "foo.b"',
                                   '"pc1" points to object "foo.c"',
                                   '"pc2" points to object "foo.c (offset +1)"',
                                   '"pc3" points to object "foo.c (offset +2)"',
                                   '"pc4" points to object "foo.c (offset +3)"',
                                   '"pd1" points to object "bar (offset +7)"',
                                   '"pd2" points to object "bar.e'])
