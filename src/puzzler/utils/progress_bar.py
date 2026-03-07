"""Progress bar utilities for training visualization."""

import time

from rich.progress import BarColumn, Progress, TaskID, TextColumn, TimeRemainingColumn


class ProgressBar:
    """A flexible progress bar with dynamic control for efficient.

    Supports both:
    - **Time-Based Updates:** Refreshes every `target_update_interval` seconds.
    - **Step-Based Updates:** Refreshes every `update_interval` steps.

    Optimized for performance using Rich's `.refresh()` and `.transient` for minimal I/O overhead.
    """

    def __init__(
        self,
        use_progress_bar: bool = True,  # noqa: FBT001, FBT002 - Boolean positional args acceptable for class initialization
        update_mode: str = "time",
        target_update_interval: float = 1.0,
    ) -> None:
        """Initializes the ProgressBar instance.

        Args:
            use_progress_bar (bool): Enables or disables the progress bar.
            update_mode (str): Mode of progress bar updates: 'time' or 'step'.
            target_update_interval (float): Time interval (in seconds) for adaptive updates.
        """
        self.use_progress_bar = use_progress_bar
        self.progress: Progress | None = None
        self.task: TaskID | None = None
        self.update_mode = update_mode
        self.target_update_interval = target_update_interval
        self.last_update_time: float = time.perf_counter()
        self.update_interval: int = 1  # Initial step size

    def __enter__(self) -> "ProgressBar":  # noqa: PYI034 - String literal return type is acceptable for forward references
        """Allows `with ProgressBar(...)` usage."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,  # noqa: PYI036 - object | None is acceptable for traceback parameter
    ) -> None:
        """Ensures `.stop()` is automatically called in `with` blocks."""
        self.stop()

    def start(self, total_batches: int, epoch: int) -> None:
        """Starts the progress bar for the given epoch.

        Args:
            total_batches (int): Total number of batches in the dataset.
            epoch (int): Current epoch number.
        """
        if self.use_progress_bar:
            self.progress = Progress(
                TextColumn("[bold blue]Epoch {task.fields[epoch]}[/]"),
                BarColumn(),
                TextColumn("• Loss: [red]{task.fields[loss]:.4f}[/]"),
                TextColumn("• Acc: [green]{task.fields[acc]:.2f}%[/]"),
                TimeRemainingColumn(),
                transient=True,
            )
            self.task = self.progress.add_task("Training", total=total_batches, loss=0.0, acc=0.0, epoch=epoch)
            self.progress.start()

    def update(self, current_batch: int, loss: float, acc: float, epoch: int, batch_time: float) -> None:
        """Update the progress bar with current metrics.

        Dynamically adjusts the update interval based on batch time (for time-based updates).

        Args:
            current_batch (int): Current batch number.
            loss (float): Average loss value for the current epoch.
            acc (float): Accuracy value for the current epoch.
            epoch (int): Current epoch number.
            batch_time (float): Time (in seconds) taken to process the current batch.
        """
        now = time.perf_counter()

        # 🔥 Adaptive Interval Adjustment
        if self.update_mode == "time":
            self.update_interval = max(1, int(self.target_update_interval / batch_time))

        # 🔥 Adaptive Progress Bar Logic
        if self.use_progress_bar and (
            (self.update_mode == "step" and current_batch % self.update_interval == 0)
            or (self.update_mode == "time" and now - self.last_update_time >= self.target_update_interval)
        ):
            if self.progress is not None and self.task is not None:
                self.progress.update(self.task, completed=current_batch, loss=loss, acc=acc, epoch=epoch)
                self.progress.refresh()
            self.last_update_time = now

    def stop(self) -> None:
        """Stops the progress bar and finalizes its output."""
        if self.use_progress_bar and self.progress is not None:
            self.progress.stop()
