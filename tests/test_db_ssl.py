import os
import shutil
import tempfile
import unittest

import numpy as np

from src.modules.neu.training.ssl_pipeline import AudioDataset, AudioNormalizer, SSLTrainer


class TestDBSSL(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_audio_normalization(self):
        y = np.array([1.0, -2.0, 0.5], dtype=np.float64)
        norm = AudioNormalizer.normalize_waveform(y)

        self.assertEqual(norm.dtype, np.float32)
        self.assertEqual(np.max(np.abs(norm)), 1.0)
        self.assertEqual(norm[1], -1.0)

    def test_fix_length(self):
        y = np.ones(10)
        padded = AudioNormalizer.fix_length(y, 15)
        self.assertEqual(len(padded), 15)
        self.assertEqual(padded[12], 0)

        cropped = AudioNormalizer.fix_length(y, 5)
        self.assertEqual(len(cropped), 5)

    def test_dataset_stub(self):
        ds = AudioDataset(["file1.wav", "file2.wav"], target_length=100)
        self.assertEqual(len(ds), 2)
        item = ds[0]
        self.assertEqual(len(item["waveform"]), 100)

    def test_trainer_checkpoint(self):
        trainer = SSLTrainer(None, self.test_dir)
        trainer.save_checkpoint(1)

        checkpoint_file = os.path.join(self.test_dir, "checkpoint_e1.txt")
        self.assertTrue(os.path.exists(checkpoint_file))


if __name__ == "__main__":
    unittest.main()
