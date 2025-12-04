import logging
import queue
import time
from .logging_config import setup_logging
from .config import load_services_config
from .worker_pool import WorkerPool
from .scheduler import SchedulerThread
from .metrics_aggregator import MetricsAggregatorThread


def run_phase5():
    setup_logging()
    logging.info("==== PHASE 5: METRICS AGGREGATOR ====")
    # python inbuilt queue-data-structure is initialized to use in thread
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    # Load services
    services = load_services_config()
    # Create worker pool instances with given details and worker-pool is start worker-work as per given worker-numbers
    pool = WorkerPool(task_queue=task_queue, results_queue=results_queue, num_workers=3)
    pool.start()
    # Metrics Aggregator
    aggregator = MetricsAggregatorThread(results_queue, services)
    aggregator.start()
    # Scheduler
    scheduler = SchedulerThread(services, task_queue)
    scheduler.start()

    logging.info("🎯 Running system for 20 seconds...")
    time.sleep(20)

    logging.info("🛑 Shutting down all threads...")

    scheduler.stop()
    scheduler.join()

    pool.stop()

    aggregator.stop()
    aggregator.join()

    logging.info("==== PHASE 5 COMPLETED ====")

run_phase5()
