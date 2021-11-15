"""
Check pointer to a class member
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestSimpleStructure(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_simple_structure(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        self.expect("vp", ordered=False, substrs=['"a" points to object "foo.A"',
                                                  '"b" points to object "foo.B"',
                                                  '"c" points to object "foo.C"'])
