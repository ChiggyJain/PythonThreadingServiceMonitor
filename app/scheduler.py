import time
import logging
from .threading_utils import StoppableThread


class SchedulerThread(StoppableThread):
    """
    This thread wakes every 1 sec and checks:
    - Which services need a new health check?
    - Based on service.interval
    """

    # constructor
    def __init__(self, services, task_queue):
        super().__init__(name="scheduler", daemon=True)
        self.services = services
        self.task_queue = task_queue
        self.last_check = {svc.name: 0 for svc in services}

    # this function will be automatically run when any respective thread-start
    # this is inbuilt function of threading.Thread class and in child is overwride as per requirement
    def run(self):
        logging.info("🕒 Scheduler started")
        while not self.stopped():
            now = time.time()
            # Loop through each service
            for svc in self.services:
                last = self.last_check[svc.name]
                # If enough time has passed → schedule a task
                if now - last >= svc.interval:
                    self.task_queue.put(svc)
                    self.last_check[svc.name] = now
                    logging.info(f"📌 Scheduled check for: {svc.name}")
            # Scheduler tick interval        
            time.sleep(1)
        logging.info("🕒 Scheduler stopped")
