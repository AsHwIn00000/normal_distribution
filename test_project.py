"""
test_project.py
===============
Comprehensive unit test suite for Network Load Statistical Analyzer.

Verifies:
1. Descriptive statistical calculations against known mathematical values.
2. Sample std dev (ddof=1) vs Population std dev (ddof=0).
3. Normal distribution CDF, exceedance probabilities, and Empirical Rule bounds.
4. Z-score normalization and edge-case handling (zero standard deviation).
5. Anomaly detection thresholding and status labeling.
6. Data validation: Missing values, non-numeric values, and duplicate handling.
"""

import math
import numpy as np
import pandas as pd
import pytest

from statistics_engine import (
    validate_network_data,
    calculate_descriptive_stats,
    calculate_z_scores,
    calculate_theoretical_probability,
    calculate_interval_probability,
    calculate_empirical_percentile,
    calculate_empirical_rule_coverage,
    assess_goodness_of_fit
)
from anomaly_detector import detect_network_anomalies


def test_descriptive_stats_known_values():
    """Verify descriptive statistics on a known textbook dataset."""
    # Data: [10, 20, 30, 40, 50]
    # N = 5
    # Mean = 30.0
    # Population Variance = (( -20^2 + -10^2 + 0 + 10^2 + 20^2 ) / 5) = (400 + 100 + 0 + 100 + 400)/5 = 1000/5 = 200.0
    # Population Std = sqrt(200) = 14.1421...
    # Sample Variance = 1000 / 4 = 250.0
    # Sample Std = sqrt(250) = 15.811388...
    # Median = 30.0
    # Min = 10.0, Max = 50.0
    data = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    
    stats_sample = calculate_descriptive_stats(data, ddof=1)
    assert stats_sample["count"] == 5
    assert math.isclose(stats_sample["mean"], 30.0, rel_tol=1e-5)
    assert math.isclose(stats_sample["sample_std"], math.sqrt(250.0), rel_tol=1e-5)
    assert math.isclose(stats_sample["sample_var"], 250.0, rel_tol=1e-5)
    assert math.isclose(stats_sample["median"], 30.0, rel_tol=1e-5)
    assert stats_sample["min"] == 10.0
    assert stats_sample["max"] == 50.0
    assert stats_sample["range"] == 40.0
    
    # Check population std
    stats_pop = calculate_descriptive_stats(data, ddof=0)
    assert math.isclose(stats_pop["population_std"], math.sqrt(200.0), rel_tol=1e-5)
    assert math.isclose(stats_pop["population_var"], 200.0, rel_tol=1e-5)
    assert stats_pop["std"] == stats_pop["population_std"]


def test_z_score_calculation():
    """Verify Z-scores against standard formula: Z = (x - mean) / std."""
    data = np.array([100.0, 110.0, 120.0, 130.0, 140.0])
    mean = 120.0
    std = float(np.std(data, ddof=1))
    
    z_scores = calculate_z_scores(data, mean=mean, std=std)
    # The center element 120.0 should have Z = 0
    assert math.isclose(z_scores[2], 0.0, abs_tol=1e-7)
    # The lowest element 100.0 should have negative Z
    assert z_scores[0] < 0
    # The highest element 140.0 should have positive Z
    assert z_scores[4] > 0
    # Symmetric property
    assert math.isclose(z_scores[0], -z_scores[4], abs_tol=1e-7)


def test_zero_variance_constant_data():
    """Verify safe handling of constant data without ZeroDivisionError."""
    constant_data = np.array([500.0, 500.0, 500.0, 500.0, 500.0])
    
    stats_res = calculate_descriptive_stats(constant_data)
    assert stats_res["sample_std"] == 0.0
    assert stats_res["variance"] == 0.0
    
    z_scores = calculate_z_scores(constant_data)
    assert len(z_scores) == 5
    assert np.all(z_scores == 0.0)
    
    # Anomaly detector should not crash on constant data
    df = pd.DataFrame({"load": constant_data})
    detection_res = detect_network_anomalies(df, "load")
    assert detection_res["is_constant"] is True
    assert detection_res["total_anomalies"] == 0


def test_theoretical_probabilities_known_cases():
    """Verify Normal distribution CDF against established reference values."""
    mean = 100.0
    std = 15.0
    
    # 1. At Mean: P(X <= mean) should be exactly 0.5 (50%)
    prob_mean = calculate_theoretical_probability(100.0, mean, std)
    assert math.isclose(prob_mean["prob_below"], 0.5, rel_tol=1e-5)
    assert math.isclose(prob_mean["prob_above"], 0.5, rel_tol=1e-5)
    assert math.isclose(prob_mean["z_score"], 0.0, abs_tol=1e-5)
    
    # 2. At Z = 1.95996 (97.5th percentile for two-tailed alpha=0.05)
    x_975 = mean + 1.95996398454 * std
    prob_975 = calculate_theoretical_probability(x_975, mean, std)
    assert math.isclose(prob_975["prob_below"], 0.975, rel_tol=1e-3)
    assert math.isclose(prob_975["prob_above"], 0.025, rel_tol=1e-3)
    
    # 3. Empirical Rule bands:
    # 1 std dev: [mean - std, mean + std] -> ~68.27%
    p_1_sigma = calculate_interval_probability(mean - std, mean + std, mean, std)
    assert math.isclose(p_1_sigma, 0.682689, rel_tol=1e-3)
    
    # 2 std dev: [mean - 2*std, mean + 2*std] -> ~95.45%
    p_2_sigma = calculate_interval_probability(mean - 2*std, mean + 2*std, mean, std)
    assert math.isclose(p_2_sigma, 0.954500, rel_tol=1e-3)
    
    # 3 std dev: [mean - 3*std, mean + 3*std] -> ~99.73%
    p_3_sigma = calculate_interval_probability(mean - 3*std, mean + 3*std, mean, std)
    assert math.isclose(p_3_sigma, 0.997300, rel_tol=1e-3)


def test_empirical_percentile():
    """Verify empirical ECDF calculation."""
    data = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    
    # Value 30.0: 3 out of 5 values are <= 30.0 -> 60%
    res = calculate_empirical_percentile(data, 30.0)
    assert res["count_below"] == 3
    assert res["count_above"] == 2
    assert math.isclose(res["empirical_pct_below"], 60.0, rel_tol=1e-5)
    
    # Value 5.0: 0 values below -> 0%
    res_low = calculate_empirical_percentile(data, 5.0)
    assert res_low["count_below"] == 0
    assert res_low["empirical_pct_below"] == 0.0


def test_anomaly_detection_logic():
    """Verify classification into Normal, Unusually High, and Unusually Low."""
    # Generate baseline data with small variance so spikes and dips have large Z scores
    # Mean ~ 100, Std ~ 5
    baseline = [100.0] * 30
    # Add a high spike (+10 std devs) and a low dip (-10 std devs)
    data = baseline + [150.0, 50.0]
    df = pd.DataFrame({"throughput": data})
    
    # Standard threshold 2.0 to detect the extreme points
    res = detect_network_anomalies(df, "throughput", z_threshold=2.0)
    
    enriched = res["enriched_df"]
    assert "z_score" in enriched.columns
    assert "anomaly_status" in enriched.columns
    
    # Index 30 is 150.0 (High spike)
    assert enriched.loc[30, "anomaly_status"] == "Unusually High"
    assert bool(enriched.loc[30, "is_anomaly"]) is True
    
    # Index 31 is 50.0 (Low dip)
    assert enriched.loc[31, "anomaly_status"] == "Unusually Low"
    assert bool(enriched.loc[31, "is_anomaly"]) is True
    
    # The baseline points should be Normal
    assert enriched.loc[0, "anomaly_status"] == "Normal"
    assert bool(enriched.loc[0, "is_anomaly"]) is False
    
    assert res["high_anomalies"] >= 1
    assert res["low_anomalies"] >= 1
    assert res["total_anomalies"] == res["high_anomalies"] + res["low_anomalies"]


def test_validation_missing_and_dirty_data():
    """Verify input validation handles NaNs, strings, and duplicates safely."""
    raw_data = {
        "timestamp": ["2026-10-01 00:00:00", "2026-10-01 00:05:00", "2026-10-01 00:10:00", "2026-10-01 00:15:00", "2026-10-01 00:15:00"],
        "bandwidth": ["100.5", "invalid_text", np.nan, "200.3", "200.3"]
    }
    df = pd.DataFrame(raw_data)
    
    res = validate_network_data(df, "bandwidth", timestamp_column="timestamp")
    assert res["is_valid"] is True
    assert res["total_rows"] == 5
    # "invalid_text" and np.nan are filtered out
    assert res["missing_count"] == 2
    assert res["valid_observations"] == 3
    assert res["duplicate_count"] == 1  # Last row is duplicate of preceding
    
    # Values should be [100.5, 200.3, 200.3]
    assert len(res["load_values"]) == 3
    assert math.isclose(res["load_values"][0], 100.5)


def test_validation_empty_or_missing_column():
    """Verify validation returns friendly error messages on bad inputs."""
    # Empty df
    res_empty = validate_network_data(pd.DataFrame(), "bandwidth")
    assert res_empty["is_valid"] is False
    assert "empty" in res_empty["error_message"].lower()
    
    # Missing column
    df = pd.DataFrame({"colA": [1, 2, 3]})
    res_col = validate_network_data(df, "non_existent_column")
    assert res_col["is_valid"] is False
    assert "not found" in res_col["error_message"].lower()


def test_empirical_rule_coverage():
    """Verify Empirical Rule coverage computation on generated sample data."""
    # Standard normal generated array
    np.random.seed(123)
    normal_data = np.random.normal(loc=500.0, scale=50.0, size=1000)
    mean = float(np.mean(normal_data))
    std = float(np.std(normal_data, ddof=1))
    
    bands = calculate_empirical_rule_coverage(normal_data, mean, std)
    assert "1_sigma" in bands
    assert "2_sigma" in bands
    assert "3_sigma" in bands
    
    # 1-sigma empirical should be close to 68.27% (within ~4% tolerance for N=1000)
    assert abs(bands["1_sigma"]["observed_pct"] - 68.27) < 4.0
    # 2-sigma empirical should be close to 95.45%
    assert abs(bands["2_sigma"]["observed_pct"] - 95.45) < 3.0
    # 3-sigma empirical should be close to 99.73%
    assert abs(bands["3_sigma"]["observed_pct"] - 99.73) < 2.0


def test_goodness_of_fit():
    """Verify Goodness-of-fit assessment on normal vs uniform data."""
    np.random.seed(42)
    # Truly normal data
    norm_data = np.random.normal(loc=0.0, scale=1.0, size=200)
    res_norm = assess_goodness_of_fit(norm_data, float(np.mean(norm_data)), float(np.std(norm_data, ddof=1)))
    assert res_norm["applicable"] is True
    # KS test p-value should typically be > 0.05 for genuine standard normal
    assert res_norm["ks_pvalue"] > 0.01

    # Clearly non-normal data (Uniform distribution)
    uniform_data = np.random.uniform(low=0.0, high=100.0, size=500)
    res_unif = assess_goodness_of_fit(uniform_data, float(np.mean(uniform_data)), float(np.std(uniform_data, ddof=1)))
    # Shapiro-Wilk will strongly reject normality (p < 0.05)
    assert res_unif["shapiro_pvalue"] < 0.05
    assert res_unif["shapiro_is_normal"] is False
