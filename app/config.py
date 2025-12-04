import yaml
from .models import ServiceConfig


def load_services_config(path: str = "config/services.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    services = []
    for s in data["services"]:
        services.append(ServiceConfig(
            name=s["name"],
            url=s["url"],
            timeout=s["timeout"],
            interval=s["interval"],
            alert_threshold=s["alert_threshold"]
        ))
    return services
