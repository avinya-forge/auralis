import unittest

import numpy as np

from src.modules.neu.training.ssl_pipeline import AudioNormalizer, ContrastiveLoss


class TestSSLPipeline(unittest.TestCase):
    def test_augment_waveform(self):
        y = np.zeros(100)
        augmented = AudioNormalizer.augment_waveform(y, noise_level=0.1)
        self.assertEqual(augmented.shape, (100,))
        self.assertFalse(np.array_equal(y, augmented))

    def test_contrastive_loss_no_torch(self):
        # We simulate what happens if torch is None
        loss_fn = ContrastiveLoss()

        # We need to temporarily hide torch
        import src.modules.neu.training.ssl_pipeline as sp

        orig_torch = sp.torch
        sp.torch = None

        try:
            result = loss_fn.forward(None, None)
            self.assertEqual(result, 0.0)
        finally:
            sp.torch = orig_torch


if __name__ == "__main__":
    unittest.main()
