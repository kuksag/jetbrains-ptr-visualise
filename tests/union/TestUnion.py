"""
Check union data type
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestUnion(TestBase):
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

        self.expect("vp", ordered=False, substrs=['"pointer_foo_a" points to "foo.A"',
                                                  '"pointer_bar_b" points to "bar.B"',

                                                  '"pointer_baz_x" points to "baz.A.x"',
                                                  '''"pointer_baz_y" points to "['baz.A.y', 'baz.B.z']"''',
                                                  '''"void_pointer_baz_x" points to "['baz', 'baz.A', 'baz.A.x', 'baz.B', 'baz.B.w']"''',
                                                  '''"void_pointer_baz_y" points to "['baz.A.y', 'baz.B.z']"''',

                                                  '"pointer_qux_w" points to "qux.B.w"',
                                                  '''"pointer_qux_z" points to "['qux.A.y', 'qux.B.z']"''',
                                                  '''"void_qux_w" points to "['qux', 'qux.A', 'qux.A.x', 'qux.B', 'qux.B.w']"''',
                                                  '''"void_qux_z" points to "['qux.A.y', 'qux.B.z']"'''])
