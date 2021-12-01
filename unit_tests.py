import unittest
import script


class TestThreadBinSearch(unittest.TestCase):
    threads = [3, 9]
    ranges = [(1, 3), (5, 5)]

    def test_match(self):
        self.assertEqual(script.get_thread_for_pointer(1, self.threads, self.ranges), 3)
        self.assertEqual(script.get_thread_for_pointer(2, self.threads, self.ranges), 3)
        self.assertEqual(script.get_thread_for_pointer(3, self.threads, self.ranges), 3)
        self.assertEqual(script.get_thread_for_pointer(5, self.threads, self.ranges), 9)

    def test_no_match(self):
        self.assertEqual(script.get_thread_for_pointer(0, self.threads, self.ranges), None)
        self.assertEqual(script.get_thread_for_pointer(4, self.threads, self.ranges), None)
        self.assertEqual(script.get_thread_for_pointer(6, self.threads, self.ranges), None)
        self.assertEqual(script.get_thread_for_pointer(100000, self.threads, self.ranges), None)
        self.assertEqual(script.get_thread_for_pointer(-100000, self.threads, self.ranges), None)


if __name__ == '__main__':
    unittest.main()
