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

        self.expect("vp", ordered=False, substrs=['"ptr_foo" points to "foo"',
                                                  '"ptr_foo_a" points to "foo.A"',
                                                  '''"void_foo" points to "['foo', 'foo.A']"'''])
