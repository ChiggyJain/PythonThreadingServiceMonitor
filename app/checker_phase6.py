import logging
import queue
import time
from .logging_config import setup_logging
from .config import load_services_config
from .worker_pool import WorkerPool
from .scheduler import SchedulerThread
from .metrics_aggregator import MetricsAggregatorThread
from .snapshot_thread import SnapshotThread


def run_phase6():
    # doing setup for inbuilt python logger as info level only
    setup_logging()
    logging.info("==== PHASE 6: SNAPSHOT PERSISTENCE LAYER ====")
    # python inbuilt queue-data-structure is initialized to use in thread
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    # Load services
    services = load_services_config()

    # Create worker pool instances with given details and worker-pool is start worker-work as per given worker-numbers
    pool = WorkerPool(
        task_queue=task_queue,
        results_queue=results_queue,
        num_workers=3
    )
    pool.start()

    # Metrics aggregator thread
    aggregator = MetricsAggregatorThread(results_queue, services)
    aggregator.start()

    # Snapshot thread (every 5 seconds)
    snapshotter = SnapshotThread(aggregator, interval=5)
    snapshotter.start()

    # Scheduler thread
    scheduler = SchedulerThread(services, task_queue)
    scheduler.start()

    logging.info("🎯 Running monitoring engine for 25 seconds...")
    time.sleep(25)

    logging.info("🛑 Stopping all components...")

    scheduler.stop()
    scheduler.join()

    snapshotter.stop()
    snapshotter.join()

    pool.stop()

    aggregator.stop()
    aggregator.join()

    logging.info("==== PHASE 6 COMPLETED ====")

run_phase6()