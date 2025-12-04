import logging
import queue
import time
from .logging_config import setup_logging
from .config import load_services_config
from .worker_pool import WorkerPool
from .scheduler import SchedulerThread
from .metrics_aggregator import MetricsAggregatorThread
from .snapshot_thread import SnapshotThread
from .alerting import AlertingThread


def run_phase7():
    # doing setup for inbuilt python logger as info level only
    setup_logging()
    logging.info("==== PHASE 7: ALERTING ENGINE ====")
    # python inbuilt queue-data-structure is initialized to use in thread
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    # Load services
    services = load_services_config()

    # Create worker pool instances with given details and worker-pool is start worker-work as per given worker-numbers
    pool = WorkerPool(
        task_queue=task_queue,
        results_queue=results_queue,
        num_workers=3,
    )
    pool.start()

    # Aggregator
    aggregator = MetricsAggregatorThread(results_queue, services)
    aggregator.start()

    # Snapshotter
    snapshotter = SnapshotThread(aggregator, interval=5)
    snapshotter.start()

    # Alerting
    alerting = AlertingThread(aggregator, services, interval=2)
    alerting.start()

    # Scheduler
    scheduler = SchedulerThread(services, task_queue)
    scheduler.start()

    logging.info("🎯 Monitoring engine running for 30 seconds...")
    time.sleep(30)

    logging.info("🛑 Shutting down all system threads...")

    scheduler.stop()
    scheduler.join()

    snapshotter.stop()
    snapshotter.join()

    alerting.stop()
    alerting.join()

    pool.stop()

    aggregator.stop()
    aggregator.join()

    logging.info("==== PHASE 7 COMPLETED ====")

run_phase7()