"""
anomaly_detector.py
===================
Z-Score based anomaly detection for network load observations.

Key concepts:
- Standardization: Z = (x - mean) / std
- Multi-tier classification:
    * Unusually High: Z > +threshold (bursts, DDoS, heavy sync, batch jobs)
    * Unusually Low:  Z < -threshold (link drop, failover, node idle, partition)
    * Normal:         -threshold <= Z <= +threshold
- Reliability:
    * Handles zero standard deviation safely
    * Non-alarmist classification (anomalies != cyberattacks)
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from statistics_engine import calculate_z_scores


def detect_network_anomalies(
    df: pd.DataFrame,
    load_column: str,
    z_threshold: float = 3.0,
    timestamp_column: Optional[str] = None,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    ddof: int = 1
) -> Dict[str, Any]:
    """
    Analyzes network load measurements and tags statistical anomalies.
    
    Parameters:
    - df: DataFrame containing network data
    - load_column: Column name for numerical load metric
    - z_threshold: Critical Z-score threshold (standard default: 3.0)
    - timestamp_column: Optional column for timestamps
    - mean, std: Precomputed statistics (optional)
    - ddof: Degrees of freedom for sample (1) vs population (0) std dev
    
    Returns:
    - Dictionary with enriched DataFrame, summary counts, and domain notes.
    """
    if df.empty or load_column not in df.columns:
        raise ValueError("Invalid DataFrame or missing load column for anomaly detection.")

    result_df = df.copy()
    # Explicit 1-based observation index for clear table presentation
    result_df["observation_index"] = np.arange(1, len(result_df) + 1)
    load_values = pd.to_numeric(result_df[load_column], errors="coerce").to_numpy(dtype=float)
    n = len(load_values)

    if mean is None:
        mean = float(np.mean(load_values))
    if std is None:
        std = float(np.std(load_values, ddof=ddof)) if (n > 1 or ddof == 0) else 0.0

    # Compute Z-scores safely
    z_scores = calculate_z_scores(load_values, mean=mean, std=std, ddof=ddof)
    result_df["z_score"] = np.round(z_scores, 3)

    # Handle zero variance / constant data
    if std <= 1e-9:
        result_df["anomaly_status"] = "Normal (Constant Data)"
        result_df["is_anomaly"] = False
        result_df["alert_level"] = "INFO"
        return {
            "enriched_df": result_df,
            "anomalies_df": pd.DataFrame(),
            "total_anomalies": 0,
            "high_anomalies": 0,
            "low_anomalies": 0,
            "anomaly_rate_pct": 0.0,
            "z_threshold": z_threshold,
            "mean": mean,
            "std": std,
            "is_constant": True,
            "disclaimer": "All network load observations are identical (Zero Variance). No statistical variation present."
        }

    # Classify each observation based on configured threshold
    status_list = []
    is_anomaly_list = []
    alert_level_list = []

    for z in z_scores:
        abs_z = abs(z)
        if z > z_threshold:
            status_list.append("Unusually High")
            is_anomaly_list.append(True)
            alert_level_list.append("HIGH_ALERT" if abs_z > 4.0 else "WARNING")
        elif z < -z_threshold:
            status_list.append("Unusually Low")
            is_anomaly_list.append(True)
            alert_level_list.append("HIGH_ALERT" if abs_z > 4.0 else "WARNING")
        else:
            status_list.append("Normal")
            is_anomaly_list.append(False)
            alert_level_list.append("NORMAL")

    result_df["anomaly_status"] = status_list
    result_df["is_anomaly"] = is_anomaly_list
    result_df["alert_level"] = alert_level_list

    # Separate anomalies table
    anomalies_df = result_df[result_df["is_anomaly"]].copy()

    total_anomalies = int(len(anomalies_df))
    high_anomalies = int((result_df["anomaly_status"] == "Unusually High").sum())
    low_anomalies = int((result_df["anomaly_status"] == "Unusually Low").sum())
    anomaly_rate_pct = (total_anomalies / n) * 100.0 if n > 0 else 0.0

    # Domain context disclaimer
    disclaimer = (
        "Engineering Note for Distributed Systems: "
        "A statistical anomaly indicates a significant mathematical deviation from the baseline model, "
        "but does NOT automatically prove a malicious cyberattack or hardware failure. "
        "High load may result from planned data backups, distributed consensus elections, or scheduled ETL jobs. "
        "Low load may indicate server maintenance, routing shift, or off-peak inactivity."
    )

    return {
        "enriched_df": result_df,
        "anomalies_df": anomalies_df,
        "total_anomalies": total_anomalies,
        "high_anomalies": high_anomalies,
        "low_anomalies": low_anomalies,
        "anomaly_rate_pct": round(anomaly_rate_pct, 2),
        "z_threshold": z_threshold,
        "mean": mean,
        "std": std,
        "is_constant": False,
        "disclaimer": disclaimer
    }
