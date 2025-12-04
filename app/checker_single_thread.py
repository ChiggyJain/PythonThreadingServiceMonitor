import time
import logging
import requests

from .config import load_services_config
from .models import CheckResult
from .logging_config import setup_logging


def perform_health_check(service):
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


def run_single_thread_checker():
    setup_logging()
    logging.info("🔍 Starting Single-Thread Health Checker")
    # getting all services in list to check health-status and other details
    services = load_services_config()
    for svc in services:
        # checking each http-services health-check status and other details
        result = perform_health_check(svc)
        if result.error:
            logging.error(f"[{svc.name}] ❌ Error: {result.error}")
        else:
            logging.info(
                f"[{svc.name}] ✅ {result.status_code} "
                f"Latency: {result.response_time_ms:.2f} ms"
            )
    logging.info("🏁 Completed Single-Thread Health Check")

run_single_thread_checker()