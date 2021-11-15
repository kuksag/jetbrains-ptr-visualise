"""
Check nested structure
"""

from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *

PATH_TO_SCRIPT = '../../script.py'


class TestStressTest(TestBase):
    mydir = TestBase.compute_mydir(__file__)

    @no_debug_info_test
    def test_stress_test(self):
        self.build()
        self.main_source_file = lldb.SBFileSpec("main.cpp")
        self.run_test()

    def run_test(self):
        self.runCmd(f"command script import {PATH_TO_SCRIPT} --allow-reload")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(self,
                                                                            "Set a breakpoint here",
                                                                            self.main_source_file)

        for i in range(target.FindFirstGlobalVariable('THREADS').data.uint32s[0]):
            ptrs = target.FindFirstGlobalVariable('ptrs')
            for j in range(target.FindFirstGlobalVariable('counter').data.uint32s[0]):
                for var in ptrs.children[:j]:
                    ptr = var.data.uint64s[0]
                    self.runCmd(f"tp {ptr}")
                    # self.expect(f"tp {ptr}", substrs=['a'])
            process.Continue()
