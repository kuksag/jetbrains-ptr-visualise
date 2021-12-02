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

        self.expect("vp", substrs=['''"ptr_a" points to "['foo', 'foo.a']"''',
                                   '''"ptr_a_1" points to "['foo + 0x1', 'foo.a + 0x1']"''',
                                   '''"ptr_b" points to "foo.b"''',
                                   '''"ptr_c" points to "foo.c"''',
                                   '''"ptr_c_1" points to "['foo + 0x4', 'foo.c + 0x1']"''',
                                   '''"ptr_c_2" points to "['foo + 0x5', 'foo.c + 0x2']"''',
                                   '''"ptr_c_3" points to "['foo + 0x6', 'foo.c + 0x3']"''',

                                   '''"ptr_bar_7" points to "bar + 0x7"''',
                                   '''"ptr_e" points to "bar.e"'''])
