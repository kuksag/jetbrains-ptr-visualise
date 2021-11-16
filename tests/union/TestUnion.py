"""
Check union data type
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class UnionTest(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_union(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        self.expect("vp", substrs=['"pa" points to object "a.A", that located in "main"',
                                   '"pb" points to object "b.B", that located in "main"'])