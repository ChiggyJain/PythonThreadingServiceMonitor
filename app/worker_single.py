import time
import logging
import queue
import requests

from .threading_utils import StoppableThread
from .models import CheckResult


class SingleWorker(StoppableThread):
    
    def __init__(self, task_queue, name="Worker1", daemon=True):
        # calling parent class constructor
        super().__init__(name=name, daemon=daemon)
        self.task_queue = task_queue

    # this function will be automatically run when any respective thread-start
    # this is inbuilt function of threading.Thread class and in child is overwride as per requirement
    def run(self):
        logging.info(f"🧵 {self.name} started")
        # this loop will be infinite till thread stop function is not called via event-signal
        while not self.stopped():
            try:
                # Wait for a task
                service = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue   # No task → loop continues
            # If we got a "None" task → indicates shutdown
            if service is None:
                self.task_queue.task_done()
                break
            # fetching the http-service response details like checking health-status and other details
            result = self.perform_health_check(service)
            # Print result (later we push to result-queue)
            if result.error:
                logging.error(
                    f"[{service.name}] ❌ Error: {result.error}"
                )
            else:
                logging.info(
                    f"[{service.name}] ✅ {result.status_code} "
                    f"Latency: {result.response_time_ms:.2f} ms"
                )
            self.task_queue.task_done()
        logging.info(f"🧵 {self.name} stopped")

    def perform_health_check(self, service):
        start = time.time()
        try:
            # http-get-request is calling
            response = requests.get(service.url, timeout=service.timeout)
            latency = (time.time() - start) * 1000
            # returning class-instances-object
            return CheckResult(
                service=service.name,
                status_code=response.status_code,
                response_time_ms=latency,
                error=None
            )
        except Exception as e:
            # returning class-instances-object
            latency = (time.time() - start) * 1000
            return CheckResult(
                service=service.name,
                status_code=None,
                response_time_ms=latency,
                error=str(e)
            )
