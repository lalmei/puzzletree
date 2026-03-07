"""Tests for progress bar utilities."""

from unittest.mock import patch

from puzzler.utils.progress_bar import ProgressBar


class TestProgressBarInit:
    """Test ProgressBar initialization."""

    def test_init_defaults(self) -> None:
        """Test default initialization."""
        pb = ProgressBar()
        assert pb.use_progress_bar is True
        assert pb.update_mode == "time"
        assert pb.target_update_interval == 1.0
        assert pb.progress is None
        assert pb.task is None
        assert pb.update_interval == 1

    def test_init_disabled(self) -> None:
        """Test initialization with progress bar disabled."""
        pb = ProgressBar(use_progress_bar=False)
        assert pb.use_progress_bar is False

    def test_init_step_mode(self) -> None:
        """Test initialization with step update mode."""
        pb = ProgressBar(update_mode="step", target_update_interval=0.5)
        assert pb.update_mode == "step"
        assert pb.target_update_interval == 0.5


class TestProgressBarContextManager:
    """Test ProgressBar as context manager."""

    def test_enter_returns_self(self) -> None:
        """Test __enter__ returns self."""
        pb = ProgressBar()
        with pb as ctx:
            assert ctx is pb

    def test_exit_calls_stop(self) -> None:
        """Test __exit__ calls stop."""
        pb = ProgressBar(use_progress_bar=True)
        with patch.object(pb, "stop") as mock_stop:
            with pb:
                pass
            mock_stop.assert_called_once()


class TestProgressBarStart:
    """Test ProgressBar start method."""

    def test_start_when_disabled(self) -> None:
        """Test start when use_progress_bar is False does nothing."""
        pb = ProgressBar(use_progress_bar=False)
        pb.start(total_batches=10, epoch=1)
        assert pb.progress is None
        assert pb.task is None

    def test_start_when_enabled(self) -> None:
        """Test start when use_progress_bar is True creates progress."""
        pb = ProgressBar(use_progress_bar=True)
        pb.start(total_batches=10, epoch=1)
        assert pb.progress is not None
        assert pb.task is not None
        pb.stop()


class TestProgressBarUpdate:
    """Test ProgressBar update method."""

    def test_update_when_disabled(self) -> None:
        """Test update when use_progress_bar is False does nothing."""
        pb = ProgressBar(use_progress_bar=False)
        pb.update(
            current_batch=1,
            loss=0.5,
            acc=90.0,
            epoch=1,
            batch_time=0.1,
        )
        assert pb.progress is None

    def test_update_step_mode(self) -> None:
        """Test update in step mode."""
        pb = ProgressBar(use_progress_bar=True, update_mode="step")
        pb.start(total_batches=10, epoch=1)
        try:
            pb.update(
                current_batch=2,
                loss=0.4,
                acc=92.0,
                epoch=1,
                batch_time=0.1,
            )
        finally:
            pb.stop()

    def test_update_time_mode(self) -> None:
        """Test update in time mode."""
        pb = ProgressBar(use_progress_bar=True, update_mode="time", target_update_interval=0.01)
        pb.start(total_batches=10, epoch=1)
        try:
            pb.update(
                current_batch=1,
                loss=0.5,
                acc=90.0,
                epoch=1,
                batch_time=0.001,
            )
        finally:
            pb.stop()

    def test_update_before_start_progress_none(self) -> None:
        """Test update when use_progress_bar is True but start() was never called."""
        pb = ProgressBar(use_progress_bar=True)
        # Call update before start - progress and task are None
        pb.update(
            current_batch=1,
            loss=0.5,
            acc=90.0,
            epoch=1,
            batch_time=0.1,
        )
        assert pb.progress is None
        assert pb.task is None


class TestProgressBarStop:
    """Test ProgressBar stop method."""

    def test_stop_when_no_progress(self) -> None:
        """Test stop when progress was never started."""
        pb = ProgressBar(use_progress_bar=False)
        pb.stop()
        assert pb.progress is None

    def test_stop_when_progress_started(self) -> None:
        """Test stop when progress was started."""
        pb = ProgressBar(use_progress_bar=True)
        pb.start(total_batches=10, epoch=1)
        pb.stop()
        assert pb.progress is not None
