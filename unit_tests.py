import unittest
import script
import attr


class TestThreadBinSearch(unittest.TestCase):

    def test_match(self):
        threads = [3, 9]
        ranges = [(1, 3), (5, 5)]
        self.assertEqual(script.get_thread_for_pointer(1, threads, ranges), 3)
        self.assertEqual(script.get_thread_for_pointer(2, threads, ranges), 3)
        self.assertEqual(script.get_thread_for_pointer(3, threads, ranges), 3)
        self.assertEqual(script.get_thread_for_pointer(5, threads, ranges), 9)

    def test_no_match(self):
        threads = [3, 9]
        ranges = [(1, 3), (5, 5)]
        self.assertEqual(script.get_thread_for_pointer(0, threads, ranges), None)
        self.assertEqual(script.get_thread_for_pointer(4, threads, ranges), None)
        self.assertEqual(script.get_thread_for_pointer(6, threads, ranges), None)
        self.assertEqual(script.get_thread_for_pointer(100000, threads, ranges), None)
        self.assertEqual(script.get_thread_for_pointer(-100000, threads, ranges), None)


@attr.s
class FrameI:
    CFA = attr.ib()

    def GetCFA(self):
        return self.CFA


@attr.s
class ThreadI:
    frames = attr.ib()

    def GetFrameAtIndex(self, idx):
        return self.frames[idx]

    def GetNumFrames(self):
        return len(self.frames)


class TestFrameBinSearch(unittest.TestCase):

    def test_match(self):
        thread = ThreadI(frames=[FrameI(CFA=3),
                                 FrameI(CFA=9),
                                 FrameI(CFA=100)])

        self.assertEqual(script.get_frame_for_pointer(0, thread), thread.GetFrameAtIndex(0))
        self.assertEqual(script.get_frame_for_pointer(2, thread), thread.GetFrameAtIndex(0))

        self.assertEqual(script.get_frame_for_pointer(3, thread), thread.GetFrameAtIndex(1))
        self.assertEqual(script.get_frame_for_pointer(4, thread), thread.GetFrameAtIndex(1))
        self.assertEqual(script.get_frame_for_pointer(8, thread), thread.GetFrameAtIndex(1))

        self.assertEqual(script.get_frame_for_pointer(9, thread), thread.GetFrameAtIndex(2))
        self.assertEqual(script.get_frame_for_pointer(10, thread), thread.GetFrameAtIndex(2))
        self.assertEqual(script.get_frame_for_pointer(99, thread), thread.GetFrameAtIndex(2))

    def test_no_match(self):
        thread = ThreadI(frames=[FrameI(CFA=3),
                                 FrameI(CFA=9),
                                 FrameI(CFA=100)])

        self.assertEqual(script.get_frame_for_pointer(100, thread), None)
        self.assertEqual(script.get_frame_for_pointer(101, thread), None)
        self.assertEqual(script.get_frame_for_pointer(10000, thread), None)


if __name__ == '__main__':
    unittest.main()
