"""
Check script with derived/base classes
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestPolymorphism(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_polymorphism(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        self.expect("vp", ordered=False,
                    substrs=['"bar" points to object "baz.Bar"',
                             '"foo" points to object "baz.Bar.Foo", that located in "main"',
                             '"a" points to object "baz.Bar.Foo.A"',
                             '"b" points to object "baz.Bar.B"',
                             '"c" points to object "baz.C"'])
