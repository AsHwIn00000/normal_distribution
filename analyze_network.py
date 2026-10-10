"""
analyze_network.py
==================
Standalone Python script for Statistical Modeling of Network Load Using Normal Distribution.

Performs:
1. Loads CSV dataset using Pandas (defaults to sample_network_load.csv).
2. Primary analysis on bandwidth_mbps (with options for packet_count_per_sec and latency_ms).
3. Calculates Mean, Population Std Dev (N), Sample Std Dev (N-1), Variance, and Z-scores.
4. Generates and saves Matplotlib plots:
   - Histogram with fitted continuous Normal distribution curve (normal_distribution_fit.png)
   - Network load vs Timestamp with anomaly threshold envelopes (network_load_time_series.png)
5. Flags Unusually High and Unusually Low observations using configurable Z-score threshold.
6. Displays flagged records in a clean table (timestamp, bandwidth, z_score, status).
7. Reports total records and missing values.
8. Exports complete analyzed results to CSV (analyzed_network_load_results.csv).
9. Explains all results in beginner-friendly language for college viva demonstrations.
"""

import sys
import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from statistics_engine import (
    validate_network_data,
    calculate_descriptive_stats,
    calculate_z_scores,
    calculate_theoretical_probability,
    calculate_empirical_rule_coverage,
    assess_goodness_of_fit
)
from anomaly_detector import detect_network_anomalies


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_cli_analysis(
    csv_file="sample_network_load.csv",
    variable="bandwidth_mbps",
    z_threshold=3.0,
    save_plots=True,
    output_csv="analyzed_network_load_results.csv"
):
    print("=" * 80)
    print("[*] STATISTICAL MODELING OF NETWORK LOAD USING NORMAL DISTRIBUTION")
    print("=" * 80)
    print(f"[+] Loading dataset: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"[!] Error: File '{csv_file}' not found.")
        return

    # 1. Load CSV using Pandas
    df_raw = pd.read_csv(csv_file)
    total_records = len(df_raw)
    
    print(f"[+] Successfully loaded {total_records} raw records.")
    print(f"    Available columns: {list(df_raw.columns)}\n")

    # 2. Variable Selection & Unit Identification
    if variable not in df_raw.columns:
        print(f"❌ Error: Column '{variable}' not found in dataset. Using 'bandwidth_mbps' instead.")
        variable = "bandwidth_mbps"

    unit_map = {
        "bandwidth_mbps": "Mbps",
        "packet_count_per_sec": "Packets/s",
        "latency_ms": "ms",
        "cpu_utilization_percent": "%"
    }
    unit = unit_map.get(variable, "units")

    # 3. Data Validation & Missing Value Check
    timestamp_col = "timestamp" if "timestamp" in df_raw.columns else None
    val_res = validate_network_data(df_raw, variable, timestamp_column=timestamp_col)
    
    if not val_res["is_valid"]:
        print(f"❌ Data Validation Error: {val_res['error_message']}")
        return

    clean_df = val_res["clean_df"]
    load_values = val_res["load_values"]
    valid_n = val_res["valid_observations"]
    missing_n = val_res["missing_count"]
    duplicate_n = val_res["duplicate_count"]

    print("--------------------------------------------------------------------------------")
    print("SECTION 1: DATASET INTEGRITY & VALIDATION REPORT")
    print("--------------------------------------------------------------------------------")
    print(f"  • Total Records in CSV:     {total_records}")
    print(f"  • Missing / NaN Values:     {missing_n}")
    print(f"  • Duplicate Rows:           {duplicate_n}")
    print(f"  • Valid Analyzed Records:   {valid_n}")
    print(f"  • Target Variable:          {variable} ({unit})")
    print("  • Explanation: Missing or invalid entries were dropped to prevent statistical skew.")
    print("--------------------------------------------------------------------------------\n")

    # 4. Statistical Calculations (Mean, Pop Std, Sample Std, Variance, Z-scores)
    stats_dict = calculate_descriptive_stats(load_values, ddof=1)
    mean_val = stats_dict["mean"]
    sample_std = stats_dict["sample_std"]
    pop_std = stats_dict["population_std"]
    sample_var = stats_dict["sample_var"]
    pop_var = stats_dict["population_var"]
    min_val = stats_dict["min"]
    max_val = stats_dict["max"]
    median_val = stats_dict["median"]
    iqr_val = stats_dict["iqr"]
    skew_val = stats_dict["skewness"]
    kurt_val = stats_dict["kurtosis"]

    print("--------------------------------------------------------------------------------")
    print("SECTION 2: STATISTICAL PARAMETERS ESTIMATION")
    print("--------------------------------------------------------------------------------")
    print(f"  * Sample Mean (x_bar):          {mean_val:.2f} {unit}")
    print(f"    -> Baseline central tendency of network load.")
    print(f"  * Sample Standard Dev (s):      {sample_std:.2f} {unit}  (N - 1 = {valid_n - 1} degrees of freedom)")
    print(f"    -> Measures typical fluctuation; uses Bessel's correction to remove sample bias.")
    print(f"  * Population Standard Dev (sigma): {pop_std:.2f} {unit}  (N = {valid_n})")
    print(f"    -> Used only if dataset represents 100% of all traffic over the network's life.")
    print(f"  * Sample Variance (s^2):        {sample_var:.2f} {unit}^2")
    print(f"  * Population Variance (sigma^2): {pop_var:.2f} {unit}^2")
    print(f"  * Minimum Value:                {min_val:.2f} {unit}")
    print(f"  * Maximum Value:                {max_val:.2f} {unit}")
    print(f"  * Median (Q2):                  {median_val:.2f} {unit}")
    print(f"  * Interquartile Range (IQR):    {iqr_val:.2f} {unit}")
    print(f"  * Sample Skewness:              {skew_val:.3f} (Normal = 0; near 0 confirms symmetry)")
    print(f"  * Excess Kurtosis:              {kurt_val:.3f} (Normal = 0; near 0 confirms light tails)")
    print("--------------------------------------------------------------------------------\n")

    # 5. Anomaly Detection using Z-Score Threshold
    detection_res = detect_network_anomalies(
        clean_df,
        load_column=variable,
        z_threshold=z_threshold,
        timestamp_column=timestamp_col,
        mean=mean_val,
        std=sample_std,
        ddof=1
    )
    
    enriched_df = detection_res["enriched_df"]
    anomalies_df = detection_res["anomalies_df"]
    total_anom = detection_res["total_anomalies"]
    high_anom = detection_res["high_anomalies"]
    low_anom = detection_res["low_anomalies"]
    anom_rate = detection_res["anomaly_rate_pct"]

    print("--------------------------------------------------------------------------------")
    print(f"SECTION 3: ANOMALY DETECTION REPORT (Configured Threshold: |Z| > {z_threshold})")
    print("--------------------------------------------------------------------------------")
    print(f"  * Total Flagged Anomalies:  {total_anom} ({anom_rate:.1f}% of observations)")
    print(f"  * Unusually High Spikes:    {high_anom} events (Z > +{z_threshold})")
    print(f"  * Unusually Low Dips:       {low_anom} events (Z < -{z_threshold})")
    print(f"  * Normal Operating Records: {valid_n - total_anom} ({(100 - anom_rate):.1f}%)\n")

    # Display flagged records table
    cols_to_print = []
    if timestamp_col and timestamp_col in enriched_df.columns:
        cols_to_print.append(timestamp_col)
    cols_to_print.extend([variable, "z_score", "anomaly_status", "alert_level"])

    if total_anom > 0:
        print("Flagged Observations Table:")
        print(anomalies_df[cols_to_print].to_string(index=False))
    else:
        print(f"No records exceeded the |Z| > {z_threshold} threshold.")
    
    print("\n[NOTE] Distributed Systems Interpretation:")
    print("   A statistical anomaly indicates significant mathematical deviation from the baseline.")
    print("   High load can be scheduled database backups or distributed query batches.")
    print("   Low load can be scheduled maintenance or link failover.")
    print("--------------------------------------------------------------------------------\n")

    # 6. Empirical Rule (68-95-99.7%) Check
    bands = calculate_empirical_rule_coverage(load_values, mean_val, sample_std)
    print("--------------------------------------------------------------------------------")
    print("SECTION 4: EMPIRICAL RULE (68-95-99.7%) VERIFICATION")
    print("--------------------------------------------------------------------------------")
    print(f"{'Interval Band':<20} | {'Range Limits':<24} | {'Theoretical':<12} | {'Observed Actual':<15} | {'Difference':<10}")
    print("-" * 90)
    for b_key, b_info in bands.items():
        limits_str = f"[{b_info['lower']:.2f}, {b_info['upper']:.2f}]"
        obs_str = f"{b_info['observed_pct']:.2f}% ({b_info['observed_count']}/{valid_n})"
        diff_str = f"{b_info['discrepancy_pct']:+.2f}%"
        print(f"{b_info['label']:<20} | {limits_str:<24} | {b_info['theoretical_pct']:.2f}%{'':<6} | {obs_str:<15} | {diff_str:<10}")
    print("--------------------------------------------------------------------------------\n")

    # 7. Goodness-of-Fit Tests (Kolmogorov-Smirnov & Shapiro-Wilk)
    fit_res = assess_goodness_of_fit(load_values, mean_val, sample_std)
    if fit_res.get("applicable", False):
        print("--------------------------------------------------------------------------------")
        print("SECTION 5: GOODNESS-OF-FIT ASSESSMENT (NORMALITY TESTS)")
        print("--------------------------------------------------------------------------------")
        print(f"  * Kolmogorov-Smirnov Test: D = {fit_res['ks_stat']:.4f}, p-value = {fit_res['ks_pvalue']:.4e}")
        ks_verdict = "Fail to reject H0 (Consistent with Normal)" if fit_res["ks_is_normal"] else "Reject H0 (Departure from Normal)"
        print(f"    -> Result: {ks_verdict}")
        if fit_res.get("shapiro_applicable", False) and fit_res["shapiro_pvalue"] is not None:
            print(f"  * Shapiro-Wilk Test:       W = {fit_res['shapiro_stat']:.4f}, p-value = {fit_res['shapiro_pvalue']:.4e}")
        print("--------------------------------------------------------------------------------\n")

    # 8. Plot Generation & Saving
    if save_plots:
        print("[*] Generating and saving Matplotlib statistical visualizations...")
        
        # Plot 1: Histogram + Fitted Normal Curve
        fig1, ax1 = plt.subplots(figsize=(9, 5.5), dpi=130)
        n_bins = min(35, max(12, int(np.sqrt(valid_n))))
        ax1.hist(
            load_values,
            bins=n_bins,
            density=True,
            alpha=0.55,
            color="#3B82F6",
            edgecolor="#1D4ED8",
            label="Observed Data (Histogram Density)"
        )

        x_axis = np.linspace(min_val - 0.5 * sample_std, max_val + 0.5 * sample_std, 400)
        normal_pdf = stats.norm.pdf(x_axis, loc=mean_val, scale=sample_std)
        ax1.plot(x_axis, normal_pdf, color="#DC2626", linewidth=2.5, label=f"Fitted Normal N({mean_val:.1f}, {sample_std:.1f}²)")

        # Vertical reference lines
        ax1.axvline(mean_val, color="#0F172A", linestyle="-", linewidth=1.8, label=f"Mean (μ={mean_val:.1f})")
        ax1.axvline(mean_val - sample_std, color="#10B981", linestyle="--", linewidth=1.2)
        ax1.axvline(mean_val + sample_std, color="#10B981", linestyle="--", linewidth=1.2, label="±1σ (68.3% band)")
        ax1.axvline(mean_val - 2 * sample_std, color="#F59E0B", linestyle="--", linewidth=1.2)
        ax1.axvline(mean_val + 2 * sample_std, color="#F59E0B", linestyle="--", linewidth=1.2, label="±2σ (95.5% band)")
        ax1.axvline(mean_val - 3 * sample_std, color="#EF4444", linestyle=":", linewidth=1.4)
        ax1.axvline(mean_val + 3 * sample_std, color="#EF4444", linestyle=":", linewidth=1.4, label="±3σ (99.7% band)")

        ax1.set_title(f"Network Load Distribution vs Fitted Normal Model ({variable})", fontsize=11, fontweight="bold")
        ax1.set_xlabel(f"Network Load ({unit})", fontsize=10)
        ax1.set_ylabel("Probability Density f(x)", fontsize=10)
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="upper right", fontsize=8.5)
        fig1.tight_layout()
        plot1_path = "normal_distribution_fit.png"
        fig1.savefig(plot1_path)
        plt.close(fig1)
        print(f"  * Saved Histogram & Normal Curve: '{plot1_path}'")

        # Plot 2: Time Series Plot with Anomaly Thresholds
        fig2, ax2 = plt.subplots(figsize=(11, 5), dpi=130)
        if timestamp_col and timestamp_col in clean_df.columns:
            try:
                x_time = pd.to_datetime(clean_df[timestamp_col])
                x_label = "Timestamp"
            except Exception:
                x_time = clean_df[timestamp_col].astype(str)
                x_label = f"Timestamp ({timestamp_col})"
        else:
            x_time = np.arange(valid_n)
            x_label = "Observation Sequence (Index)"

        ax2.plot(x_time, load_values, color="#64748B", linewidth=1.2, alpha=0.85, label=f"Observed {variable}")
        
        upper_limit = mean_val + z_threshold * sample_std
        lower_limit = mean_val - z_threshold * sample_std

        ax2.axhline(mean_val, color="#0F172A", linestyle="-", linewidth=1.5, label=f"Mean Baseline ({mean_val:.1f} {unit})")
        ax2.axhline(upper_limit, color="#DC2626", linestyle="--", linewidth=1.4, label=f"Upper Bound (+{z_threshold} sigma: {upper_limit:.1f})")
        ax2.axhline(lower_limit, color="#2563EB", linestyle="--", linewidth=1.4, label=f"Lower Bound (-{z_threshold} sigma: {lower_limit:.1f})")

        # Overlay anomalies
        high_idx = enriched_df["anomaly_status"] == "Unusually High"
        low_idx = enriched_df["anomaly_status"] == "Unusually Low"

        if high_idx.any():
            ax2.scatter(np.array(x_time)[high_idx], load_values[high_idx], color="#DC2626", s=60, edgecolors="black", zorder=5, label=f"Unusually High ({high_anom})")
        if low_idx.any():
            ax2.scatter(np.array(x_time)[low_idx], load_values[low_idx], color="#0284C7", s=60, edgecolors="black", zorder=5, label=f"Unusually Low ({low_anom})")

        ax2.set_title(f"Time-Series Network Load with Z-Score Anomaly Bounds (|Z| > {z_threshold})", fontsize=11, fontweight="bold")
        ax2.set_xlabel(x_label, fontsize=10)
        ax2.set_ylabel(f"Load ({unit})", fontsize=10)
        ax2.grid(True, linestyle=":", alpha=0.6)
        if isinstance(x_time, pd.Series) and pd.api.types.is_datetime64_any_dtype(x_time):
            fig2.autofmt_xdate()
        ax2.legend(loc="upper right", fontsize=8.5)
        fig2.tight_layout()
        plot2_path = "network_load_time_series.png"
        fig2.savefig(plot2_path)
        plt.close(fig2)
        print(f"  * Saved Time Series Plot:        '{plot2_path}'\n")

    # 9. Export Analyzed Dataset to CSV
    enriched_df.to_csv(output_csv, index=False)
    print(f"[+] Full analyzed results exported to: '{output_csv}'")
    print(f"    (Includes calculated Z-scores, anomaly statuses, and alert levels for all {valid_n} records)\n")

    print("=" * 80)
    print("[+] ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Statistical Modeling of Network Load Using Normal Distribution")
    parser.add_argument("--csv", default="sample_network_load.csv", help="Path to network load CSV dataset")
    parser.add_argument("--variable", default="bandwidth_mbps", choices=["bandwidth_mbps", "packet_count_per_sec", "latency_ms", "cpu_utilization_percent"], help="Variable to analyze")
    parser.add_argument("--threshold", type=float, default=3.0, help="Z-score anomaly threshold (default: 3.0)")
    parser.add_argument("--output", default="analyzed_network_load_results.csv", help="Output CSV path for results")
    args = parser.parse_args()

    run_cli_analysis(
        csv_file=args.csv,
        variable=args.variable,
        z_threshold=args.threshold,
        output_csv=args.output
    )
