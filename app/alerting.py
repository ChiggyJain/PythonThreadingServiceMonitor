import time
import logging
from .threading_utils import StoppableThread


class AlertingThread(StoppableThread):
    """
    Periodically scans metrics from MetricsAggregatorThread
    and generates alerts based on service thresholds.
    """

    # constructor
    def __init__(self, aggregator, services, interval=2):
        super().__init__(name="alerting", daemon=True)
        self.aggregator = aggregator
        self.interval = interval
        # Map service_name -> thresholds
        self.thresholds = {
            svc.name: svc.alert_threshold for svc in services
        }
        # Track active alerts to avoid spamming logs
        # { service_name: { "down": bool, "latency": bool } }
        self.active_alerts = {
            svc.name: {"down": False, "latency": False}
            for svc in services
        }

    # defined own function and not-inherit/built-in function
    def run(self):
        logging.info("🚨 Alerting Thread started")
        while not self.stopped():
            time.sleep(self.interval)
            # Take a snapshot of metrics (no lock, shallow copy)
            metrics_snapshot = {
                svc: data.copy()
                for svc, data in self.aggregator.metrics.items()
            }
            for service_name, m in metrics_snapshot.items():
                self._evaluate_service(service_name, m)
        logging.info("🚨 Alerting Thread stopped")

    # defined own function and not-inherit/built-in function
    def _evaluate_service(self, service_name, m):
        thresholds = self.thresholds.get(service_name, {})
        active = self.active_alerts[service_name]

        # 1) DOWN ALERT based on consecutive_failures
        max_fail = thresholds.get("consecutive_failures", 3)
        if m["consecutive_failures"] >= max_fail:
            if not active["down"]:
                logging.error(
                    f"🚨 ALERT: Service '{service_name}' is DOWN "
                    f"(consecutive_failures={m['consecutive_failures']})"
                )
                active["down"] = True
        else:
            # Recovery for DOWN alert
            if active["down"] and m["last_status"] == "up":
                logging.info(
                    f"✅ RECOVERY: Service '{service_name}' is back UP "
                    f"(consecutive_failures={m['consecutive_failures']})"
                )
                active["down"] = False

        # 2) LATENCY ALERT based on avg_latency_ms
        max_latency = thresholds.get("max_latency_ms")
        if max_latency is not None and m["avg_latency_ms"] > 0:
            if m["avg_latency_ms"] >= max_latency:
                if not active["latency"]:
                    logging.warning(
                        f"⚠️ LATENCY ALERT: Service '{service_name}' is SLOW "
                        f"(avg_latency={m['avg_latency_ms']:.2f} ms, "
                        f"threshold={max_latency} ms)"
                    )
                    active["latency"] = True
            else:
                # Recovery for latency
                if active["latency"]:
                    logging.info(
                        f"✅ LATENCY RECOVERY: Service '{service_name}' "
                        f"avg_latency back to normal "
                        f"({m['avg_latency_ms']:.2f} ms < {max_latency} ms)"
                    )
                    active["latency"] = False
