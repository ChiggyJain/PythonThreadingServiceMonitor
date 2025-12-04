import logging
import queue
import time
from .logging_config import setup_logging
from .config import load_services_config
from .worker_pool import WorkerPool
from .scheduler import SchedulerThread


def run_phase4():
    # doing setup for inbuilt python logger as info level only
    setup_logging()
    logging.info("==== PHASE 4: SCHEDULER THREAD + WORKER POOL ====")
    # python inbuilt queue-data-structure is initialized to use in thread
    task_queue = queue.Queue()
    # Load services
    services = load_services_config()
    # Create worker pool instances with given details and worker-pool is start worker-work as per given worker-numbers
    pool = WorkerPool(task_queue=task_queue, num_workers=3)
    pool.start()
    # Start scheduler
    scheduler = SchedulerThread(services=services, task_queue=task_queue)
    scheduler.start()

    logging.info("🎯 System running for 20 seconds...")
    time.sleep(20)

    logging.info("🛑 Shutting down scheduler and workers...")

    # Stop scheduler
    scheduler.stop()
    scheduler.join()

    # Stop worker pool
    pool.stop()

    logging.info("==== PHASE 4 COMPLETED ====")

run_phase4()    
