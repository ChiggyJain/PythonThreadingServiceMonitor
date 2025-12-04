import queue
import logging
from .worker_single import SingleWorker

class WorkerPool:

    # constructor
    def __init__(self, task_queue, results_queue=None, num_workers=3):
        self.task_queue = task_queue
        self.results_queue = results_queue
        self.num_workers = num_workers
        self.workers = []

    # defined own function and not-inherit/built-in function 
    def start(self):
        logging.info(f"🚀 Starting WorkerPool with {self.num_workers} workers")
        for i in range(self.num_workers):
            # activating each worker with respective task details
            worker = SingleWorker(
                task_queue=self.task_queue,
                results_queue=self.results_queue,
                name=f"Worker-{i+1}"
            )
            worker.start()
            # storing each worker instances into list
            self.workers.append(worker)

    # defined own function and not-inherit/built-in function
    def stop(self):
        logging.info("🛑 Stopping WorkerPool...")
        # Send stop signal via poison-pill to each acitvated worker
        for _ in self.workers:
            self.task_queue.put(None)
        # Stop thread flags to each acitvated worker
        for worker in self.workers:
            worker.stop()
        # Wait for all to finish to each acitvated worker
        for worker in self.workers:
            worker.join()
        logging.info("🏁 WorkerPool fully stopped.")
