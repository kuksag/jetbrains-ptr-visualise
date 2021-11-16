"""
Check situation when we have a pointer to the first child of object
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestStructFirstMember(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_struct_first_member(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        self.expect("vp", substrs=['"f" points to object "F", that located in "main"',
                                   '"a" points to object "F.A", that located in "main"'])
