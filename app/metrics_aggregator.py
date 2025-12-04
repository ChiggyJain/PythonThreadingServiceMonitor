import time
import logging
import queue
from .threading_utils import StoppableThread


class MetricsAggregatorThread(StoppableThread):

    # constructor
    def __init__(self, results_queue, services):
        super().__init__(name="Aggregator", daemon=True)
        self.results_queue = results_queue
        # Initialize metrics dictionary of each given services
        self.metrics = {
            svc.name: {
                "total_checks": 0,
                "success": 0,
                "failures": 0,
                "consecutive_failures": 0,
                "avg_latency_ms": 0.0,
                "last_status": "unknown"
            }
            for svc in services
        }

    # this function will be automatically run when any respective thread-start
    # this is inbuilt function of threading.Thread class and in child is overwride as per requirement
    def run(self):
        logging.info("📊 Metrics Aggregator started")
        while not self.stopped():
            try:
                result = self.results_queue.get(timeout=1)
            except queue.Empty:
                continue
            self.update_metrics(result)
            self.results_queue.task_done()
        logging.info("📊 Metrics Aggregator stopped")

    # this function update the given respective services-result in the form of metrics details only
    def update_metrics(self, result):
        m = self.metrics[result.service]
        m["total_checks"] += 1
        if result.error:
            m["failures"] += 1
            m["consecutive_failures"] += 1
            m["last_status"] = "down"
        else:
            m["success"] += 1
            m["consecutive_failures"] = 0
            m["last_status"] = "up"
            # Update rolling average latency
            old_avg = m["avg_latency_ms"]
            n = m["success"]
            m["avg_latency_ms"] = ((old_avg * (n - 1)) + result.response_time_ms) / n
        logging.info(
            f"📈 {result.service} | status={m['last_status']} | "
            f"avg_lat={m['avg_latency_ms']:.2f}ms | "
            f"checks={m['total_checks']} | "
            f"fails={m['failures']} | "
            f"consec_fails={m['consecutive_failures']}"
        )
