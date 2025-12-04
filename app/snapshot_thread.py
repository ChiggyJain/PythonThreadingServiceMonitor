import time
import logging
from .threading_utils import StoppableThread
from .storage import save_metrics_json, save_metrics_csv

class SnapshotThread(StoppableThread):
    """
    Periodically saves metrics to disk (JSON + CSV)
    """

    # constructor
    def __init__(self, aggregator, interval=5):
        super().__init__(name="snapshot", daemon=True)
        self.aggregator = aggregator
        self.interval = interval

    # defined own function and not-inherit/built-in function
    def run(self):
        logging.info("💾 Snapshot Thread started")
        while not self.stopped():
            time.sleep(self.interval)
            # Thread-safe: make a deep copy of metrics first
            snapshot = {
                svc: data.copy()
                for svc, data in self.aggregator.metrics.items()
            }
            save_metrics_json(snapshot)
            save_metrics_csv(snapshot)
            logging.info("💾 Snapshot saved to JSON and CSV")
        logging.info("💾 Snapshot Thread stopped")
