import logging
import queue
from .logging_config import setup_logging
from .config import load_services_config
from .worker_pool import WorkerPool


def run_phase3():
    # doing setup for inbuilt python logger as info level only
    setup_logging()
    logging.info("==== PHASE 3: MULTI WORKER POOL ====")
    # python inbuilt queue-data-structure is initialized to use in thread
    task_queue = queue.Queue()
    # Load services
    services = load_services_config()
    # Create worker pool instances with given details and worker-pool is start worker-work as per given worker-numbers
    pool = WorkerPool(task_queue=task_queue, num_workers=3)
    pool.start()
    # Push each tasks into queue
    for svc in services:
        task_queue.put(svc)
    # Wait for all tasks must be done from queue
    task_queue.join()
    # Shutdown worker pool and also stop each worker-instances
    pool.stop()
    logging.info("==== PHASE 3 COMPLETED ====")

run_phase3()
