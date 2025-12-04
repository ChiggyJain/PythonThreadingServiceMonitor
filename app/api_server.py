import logging
import queue
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .config import load_services_config
from .worker_pool import WorkerPool
from .scheduler import SchedulerThread
from .metrics_aggregator import MetricsAggregatorThread
from .snapshot_thread import SnapshotThread
from .alerting import AlertingThread
from .logging_config import setup_logging


app = FastAPI(title="PythonThreadingServiceMonitor API")

# Global references
task_queue = queue.Queue()
results_queue = queue.Queue()
services = load_services_config()

# Threads (initially None)
worker_pool = None
aggregator = None
scheduler = None
snapshotter = None
alerting = None


@app.on_event("startup")
def startup_event():
    global worker_pool, aggregator, scheduler, snapshotter, alerting
    setup_logging()
    logging.info("🚀 Starting Monitoring Engine via FastAPI")

    # Worker Pool
    worker_pool = WorkerPool(
        task_queue=task_queue,
        results_queue=results_queue,
        num_workers=3
    )
    worker_pool.start()

    # Aggregator
    aggregator = MetricsAggregatorThread(results_queue, services)
    aggregator.start()

    # Scheduler
    scheduler = SchedulerThread(services, task_queue)
    scheduler.start()

    # Snapshotter
    snapshotter = SnapshotThread(aggregator, interval=5)
    snapshotter.start()

    # Alerting
    alerting = AlertingThread(aggregator, services, interval=2)
    alerting.start()

    logging.info("💡 All monitoring threads started.")


@app.on_event("shutdown")
def shutdown_event():
    global worker_pool, aggregator, scheduler, snapshotter, alerting
    logging.info("🛑 Shutting down monitoring engine...")

    # Stop scheduler
    scheduler.stop()
    scheduler.join()

    # Stop snapshot
    snapshotter.stop()
    snapshotter.join()

    # Stop alerting
    alerting.stop()
    alerting.join()

    # Stop workers
    worker_pool.stop()

    # Stop aggregator
    aggregator.stop()
    aggregator.join()

    logging.info("🏁 Monitoring engine stopped cleanly.")


# ========== API ENDPOINTS ==========

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Monitoring engine running."}


@app.get("/metrics")
def get_metrics():
    # Return live metrics from aggregator
    snapshot = {
        svc: data.copy()
        for svc, data in aggregator.metrics.items()
    }
    return JSONResponse(snapshot)
