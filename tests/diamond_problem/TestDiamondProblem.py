"""
Check script with derived/base classes
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestDiamondProblem(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_diamond_problem(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        self.expect("vp", ordered=False, substrs=['"left" points to object "bottom.Left"',
                                                  '"right" points to object "bottom.Right"',
                                                  '"b" points to object "bottom.Left.B"',
                                                  '"c" points to object "bottom.Right.C"',
                                                  '"d" points to object "bottom.D"'],
                    patterns=[r'"top" points to object "bottom\.(Left|Right)\.Top"',
                              r'"a" points to object "bottom\.(Left|Right)\.Top\.A"'])
