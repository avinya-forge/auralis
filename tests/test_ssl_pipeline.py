from unittest.mock import MagicMock, patch

import numpy as np

from src.modules.neu.training.ssl_pipeline import (
    AudioDataset,
    AudioNormalizer,
    ContrastiveLoss,
    SSLPipeline,
    SSLTrainer,
)


def test_audio_normalizer():
    # normalize_waveform
    empty = np.array([])
    assert len(AudioNormalizer.normalize_waveform(empty)) == 0

    signal = np.array([0.5, -2.0, 1.0])
    norm = AudioNormalizer.normalize_waveform(signal)
    assert np.max(np.abs(norm)) == 1.0
    assert norm[1] == -1.0

    # fix_length
    short = np.ones(5)
    fixed_short = AudioNormalizer.fix_length(short, 10)
    assert len(fixed_short) == 10
    assert fixed_short[-1] == 0.0

    long = np.ones(15)
    fixed_long = AudioNormalizer.fix_length(long, 10)
    assert len(fixed_long) == 10

    exact = np.ones(10)
    assert len(AudioNormalizer.fix_length(exact, 10)) == 10

    # augment_waveform
    y = np.zeros(10)
    aug = AudioNormalizer.augment_waveform(y, noise_level=0.1)
    assert aug.shape == (10,)
    assert not np.allclose(aug, y)  # there should be some noise


def test_audio_dataset():
    files = ["file1.wav", "file2.wav"]
    dataset = AudioDataset(files, target_length=100)

    assert len(dataset) == 2

    item = dataset[0]
    assert "waveform" in item
    assert "label" in item
    assert item["waveform"].shape == (100,)
    assert item["label"] == 0


def test_ssl_trainer(tmp_path):
    output_dir = tmp_path / "checkpoints"
    trainer = SSLTrainer(model=None, output_dir=str(output_dir))

    assert trainer.train_epoch(None) == 0.5

    trainer.save_checkpoint(epoch=1)
    chkpt_path = output_dir / "checkpoint_e1.txt"
    assert chkpt_path.exists()
    assert chkpt_path.read_text() == "Epoch 1 checkpoint stub"


def test_contrastive_loss():
    # Test without torch
    loss_fn = ContrastiveLoss(temperature=0.5)
    assert loss_fn.forward(None, None) == 0.0

    # Test with torch mocked
    mock_torch = MagicMock()
    mock_F = MagicMock()

    with patch("src.modules.neu.training.ssl_pipeline.torch", mock_torch), patch(
        "src.modules.neu.training.ssl_pipeline.F", mock_F
    ):

        mock_F.normalize.side_effect = lambda x, dim: x
        mock_z1 = MagicMock()
        mock_z1.size.return_value = 4
        mock_z1.device = "cpu"

        mock_z2 = MagicMock()
        mock_mm_res = MagicMock()
        mock_torch.mm.return_value = mock_mm_res

        mock_labels = MagicMock()
        mock_torch.arange.return_value.to.return_value = mock_labels

        mock_F.cross_entropy.return_value = 1.5

        loss_val = loss_fn.forward(mock_z1, mock_z2)

        assert loss_val == 1.5
        mock_F.normalize.assert_called()
        mock_torch.mm.assert_called()
        mock_F.cross_entropy.assert_called()


def test_ssl_pipeline():
    # Test without torch (init shouldn't fail, methods should return 0.0)
    mock_model = MagicMock()
    pipeline = SSLPipeline(mock_model)

    assert pipeline.train_step(None, None) == 0.0
    assert pipeline.train_epoch([1, 2], lambda x: x) == 0.0

    # Test save/load without torch (does nothing)
    pipeline.save_checkpoint("path.pth")
    pipeline.load_checkpoint("path.pth")

    # Test with torch mocked
    mock_torch = MagicMock()
    mock_nn = MagicMock()
    mock_model2 = MagicMock()

    with patch("src.modules.neu.training.ssl_pipeline.torch", mock_torch), patch(
        "src.modules.neu.training.ssl_pipeline.nn", mock_nn
    ):

        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        mock_optim = MagicMock()
        mock_torch.optim.Adam.return_value = mock_optim

        mock_criterion = MagicMock()
        mock_nn.MSELoss.return_value = mock_criterion

        pipe_torch = SSLPipeline(mock_model2)

        # Test train_step
        mock_batch = MagicMock()
        mock_aug = MagicMock()
        mock_batch.to.return_value = mock_batch
        mock_aug.to.return_value = mock_aug

        mock_model2.return_value = "features"

        mock_loss = MagicMock()
        mock_loss.item.return_value = 2.5
        mock_criterion.return_value = mock_loss

        loss_val = pipe_torch.train_step(mock_batch, mock_aug)
        assert loss_val == 2.5
        mock_optim.zero_grad.assert_called()
        mock_loss.backward.assert_called()
        mock_optim.step.assert_called()

        # Test train_epoch
        dataloader = [mock_batch] * 12  # more than 10 to hit i % 10 == 0

        def augment(b):
            return mock_aug

        avg_loss = pipe_torch.train_epoch(dataloader, augment)
        assert avg_loss == 2.5

        # Test save
        pipe_torch.save_checkpoint("chkpt.pth")
        mock_torch.save.assert_called_once()

        # Test load
        mock_torch.load.return_value = {"model_state_dict": "msd", "optimizer_state_dict": "osd"}
        pipe_torch.load_checkpoint("chkpt.pth")
        mock_model2.load_state_dict.assert_called_with("msd")
        mock_optim.load_state_dict.assert_called_with("osd")
