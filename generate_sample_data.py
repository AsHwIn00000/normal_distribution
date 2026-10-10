"""
Generator for synthetic network load dataset.
Uses pure Python standard library (csv, math, random, datetime) so it runs
anywhere without external dependencies.

Generates a realistic 24-hour time series (every 5 minutes = 288 observations)
simulating traffic on a distributed cluster node.
"""

import csv
import math
import random
from datetime import datetime, timedelta

def generate_dataset(output_path="sample_network_load.csv"):
    # Fixed seed for deterministic, reproducible results
    random.seed(42)
    
    start_time = datetime(2026, 10, 1, 0, 0, 0)
    rows = []
    
    # 288 records = 24 hours * 12 (5-min intervals)
    for i in range(288):
        current_time = start_time + timedelta(minutes=5 * i)
        hour = current_time.hour + current_time.minute / 60.0
        
        # Diurnal pattern (daytime higher traffic ~+35 Mbps, nighttime lower)
        diurnal_offset = 35.0 * math.sin((hour - 6) * math.pi / 12)
        
        # Baseline normal noise: Mean = 450.0, Std = 28.0
        noise = random.gauss(0.0, 28.0)
        bandwidth = 450.0 + diurnal_offset + noise
        
        # Inject realistic distributed systems events
        if i == 44:
            # 03:40 AM - Unusually Low: Transient link flap / partition
            bandwidth = 220.50
        elif i == 123:
            # 10:15 AM - Unusually High: Distributed database snapshot / backup
            bandwidth = 675.80
        elif i == 174:
            # 14:30 PM - Unusually High: Large distributed MapReduce/ETL burst
            bandwidth = 620.40
        elif i == 232:
            # 19:20 PM - Unusually High: Peak client traffic spike
            bandwidth = 598.20
            
        bandwidth = round(bandwidth, 2)
        
        # Derived realistic metrics
        packet_count = int(round(bandwidth * 75.0 + random.gauss(0, 800)))
        cpu_util = round(max(5.0, min(98.0, 25.0 + (bandwidth / 10.0) + random.gauss(0, 3.0))), 1)
        latency = round(max(8.0, min(120.0, 18.0 + (bandwidth - 400.0) * 0.04 + random.gauss(0, 1.8))), 2)
        
        rows.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "bandwidth_mbps": bandwidth,
            "packet_count_per_sec": packet_count,
            "cpu_utilization_percent": cpu_util,
            "latency_ms": latency,
            "server_node_id": "node-dist-cluster-01"
        })
        
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["timestamp", "bandwidth_mbps", "packet_count_per_sec", "cpu_utilization_percent", "latency_ms", "server_node_id"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Successfully generated {len(rows)} observations in '{output_path}'.")

if __name__ == "__main__":
    generate_dataset()
