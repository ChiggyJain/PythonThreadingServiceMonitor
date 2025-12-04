import json
import csv
import time
import os

def save_metrics_json(metrics, path="snapshots/metrics.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(metrics, f, indent=4)
    os.replace(temp_path, path)


def save_metrics_csv(metrics, path="snapshots/metrics.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "service", "total_checks", "success", "failures",
            "consecutive_failures", "avg_latency_ms", "last_status"
        ])
        for svc, m in metrics.items():
            writer.writerow([
                svc,
                m["total_checks"],
                m["success"],
                m["failures"],
                m["consecutive_failures"],
                m["avg_latency_ms"],
                m["last_status"]
            ])
    os.replace(temp_path, path)
