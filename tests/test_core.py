import unittest
from sentinel_timelapse.core import Timelapse

class TestTimelapse(unittest.TestCase):

    def setUp(self):
        self.timelapse = Timelapse()

    def test_start(self):
        self.timelapse.start()
        self.assertTrue(self.timelapse.is_running)

    def test_stop(self):
        self.timelapse.start()
        self.timelapse.stop()
        self.assertFalse(self.timelapse.is_running)

    def test_process_frame(self):
        self.timelapse.start()
        frame = "test_frame_data"
        result = self.timelapse.process_frame(frame)
        self.assertEqual(result, "Processed: test_frame_data")

if __name__ == '__main__':
    unittest.main()