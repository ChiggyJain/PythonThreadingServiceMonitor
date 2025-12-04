import logging
import queue

from .config import load_services_config
from .logging_config import setup_logging
from .worker_single import SingleWorker


def run_phase2():
    # doing setup for inbuilt python logger as info level only
    setup_logging()
    logging.info("🚀 Starting Phase 2 — Single Worker + Queue")
    # python inbuilt queue-data-structure is initialized to use in thread
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    # Load monitoring config
    services = load_services_config()
    # Create & start worker thread
    worker = SingleWorker(task_queue, results_queue)
    worker.start()
    # Push all services as tasks
    for svc in services:
        task_queue.put(svc)
    # Wait until all tasks completed
    task_queue.join()
    # Stop worker thread by sending poison-pill
    task_queue.put(None)
    worker.stop()
    worker.join()
    logging.info("🏁 Phase 2 completed.")

run_phase2()   
