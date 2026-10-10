"""
statistics_engine.py
====================
Core mathematical and statistical calculations for the Network Load Analyzer.

Focus:
- Descriptive statistics (Mean, Variance, Sample vs Population Std Dev)
- Gaussian / Normal distribution modeling (PDF, CDF, Survival Function)
- Z-score normalization and standardization
- Empirical Rule (68-95-99.7%) validation
- Goodness-of-fit assessments (Kolmogorov-Smirnov & Shapiro-Wilk)
- Input dataset validation and cleaning

Designed for first-year B.Tech CSE students:
Clear, modular, well-commented, and mathematically rigorous.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats


def validate_network_data(
    df: pd.DataFrame,
    load_column: str,
    timestamp_column: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validates input dataset and extracts clean numerical series.
    
    Checks:
    - Empty dataset
    - Column presence
    - Non-numeric or missing values
    - Duplicate rows
    - Constant values (zero variance)
    
    Returns a dictionary containing clean series, clean dataframe, and validation flags.
    """
    if df is None or df.empty:
        return {
            "is_valid": False,
            "error_message": "Dataset is empty. Please upload or load a valid CSV file."
        }

    if load_column not in df.columns:
        return {
            "is_valid": False,
            "error_message": f"Selected column '{load_column}' was not found in the dataset."
        }

    total_rows = len(df)
    
    # Check duplicate rows
    duplicate_count = int(df.duplicated().sum())

    # Create working copy
    clean_df = df.copy()

    # Convert load column to numeric, coerce non-numeric values to NaN
    clean_df[load_column] = pd.to_numeric(clean_df[load_column], errors="coerce")
    
    # Missing / NaN count before dropping
    missing_count = int(clean_df[load_column].isna().sum())

    # Drop missing values in the target column
    clean_df = clean_df.dropna(subset=[load_column])
    valid_observations = len(clean_df)

    if valid_observations == 0:
        return {
            "is_valid": False,
            "error_message": f"Column '{load_column}' contains no valid numerical values."
        }

    # Extract numpy array of load values
    load_values = clean_df[load_column].to_numpy(dtype=float)

    # Check for negative values (unusual for bandwidth/packet counts)
    has_negative_values = bool(np.any(load_values < 0))

    # Check for constant data (zero variance)
    is_constant = bool(np.all(load_values == load_values[0]))

    # Handle timestamp column if provided
    timestamp_valid = False
    if timestamp_column and timestamp_column in clean_df.columns:
        try:
            clean_df["parsed_timestamp"] = pd.to_datetime(clean_df[timestamp_column], errors="coerce")
            timestamp_valid = clean_df["parsed_timestamp"].notna().any()
        except Exception:
            timestamp_valid = False

    return {
        "is_valid": True,
        "clean_df": clean_df,
        "load_values": load_values,
        "total_rows": total_rows,
        "valid_observations": valid_observations,
        "missing_count": missing_count,
        "duplicate_count": duplicate_count,
        "has_negative_values": has_negative_values,
        "is_constant": is_constant,
        "timestamp_valid": timestamp_valid,
        "timestamp_column": timestamp_column if timestamp_valid else None
    }


def calculate_descriptive_stats(
    values: np.ndarray,
    ddof: int = 1
) -> Dict[str, float]:
    """
    Computes comprehensive descriptive statistics.
    
    Mathematical Note on Standard Deviation:
    - Sample Standard Deviation (ddof=1, Bessel's Correction):
        s = sqrt( (1 / (N - 1)) * sum((x_i - mean)^2) )
      Used when analyzing a sample of network traffic to estimate the true
      population parameter without bias.
    - Population Standard Deviation (ddof=0):
        sigma = sqrt( (1 / N) * sum((x_i - mean)^2) )
      Used only if the dataset represents 100% of all traffic that ever exists.
      
    By default, we use ddof=1 (Sample Standard Deviation).
    """
    n = len(values)
    if n == 0:
        raise ValueError("Cannot compute statistics on empty data array.")

    mean_val = float(np.mean(values))
    sample_std = float(np.std(values, ddof=1)) if n > 1 else 0.0
    population_std = float(np.std(values, ddof=0))
    
    # Active standard deviation based on user parameter
    active_std = float(np.std(values, ddof=ddof)) if (n > 1 or ddof == 0) else 0.0
    
    sample_var = sample_std ** 2
    population_var = population_std ** 2
    active_var = active_std ** 2

    min_val = float(np.min(values))
    max_val = float(np.max(values))
    median_val = float(np.median(values))
    
    q1 = float(np.percentile(values, 25))
    q3 = float(np.percentile(values, 75))
    iqr = q3 - q1

    # Skewness: measures asymmetry of distribution (Normal = 0)
    skewness = float(stats.skew(values, bias=False)) if (n > 2 and active_std > 1e-9) else 0.0
    
    # Kurtosis: measures heavy tails (Normal excess kurtosis = 0)
    kurtosis = float(stats.kurtosis(values, fisher=True, bias=False)) if (n > 3 and active_std > 1e-9) else 0.0

    return {
        "count": n,
        "mean": mean_val,
        "sample_std": sample_std,
        "population_std": population_std,
        "std": active_std,
        "sample_var": sample_var,
        "population_var": population_var,
        "variance": active_var,
        "min": min_val,
        "max": max_val,
        "range": max_val - min_val,
        "median": median_val,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "ddof_used": ddof
    }


def calculate_z_scores(
    values: np.ndarray,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    ddof: int = 1
) -> np.ndarray:
    """
    Calculates the Z-score (standard score) for each observation:
        Z = (x - mean) / std
        
    Safe against zero standard deviation (constant load values).
    If std == 0, returns array of zeros.
    """
    n = len(values)
    if n == 0:
        return np.array([], dtype=float)

    if mean is None:
        mean = float(np.mean(values))
    if std is None:
        std = float(np.std(values, ddof=ddof)) if (n > 1 or ddof == 0) else 0.0

    if std <= 1e-9:
        # Constant data: all points are at the mean
        return np.zeros_like(values, dtype=float)

    return (values - mean) / std


def calculate_theoretical_probability(
    x_val: float,
    mean: float,
    std: float
) -> Dict[str, float]:
    """
    Estimates probabilities under the fitted Normal distribution N(mean, std^2).
    
    Formulas:
    - Standard score: Z = (x - mean) / std
    - Cumulative probability (below or equal to x):
        P(X <= x) = Phi(Z) = 0.5 * [1 + erf(Z / sqrt(2))]
    - Exceedance probability (above x):
        P(X > x) = 1 - Phi(Z)
    """
    if std <= 1e-9:
        # Degenerate normal distribution (zero variance)
        if x_val < mean:
            prob_below = 0.0
            prob_above = 1.0
            z_score = -np.inf
        elif x_val > mean:
            prob_below = 1.0
            prob_above = 0.0
            z_score = np.inf
        else:
            prob_below = 1.0
            prob_above = 0.0
            z_score = 0.0
        return {
            "x_val": x_val,
            "z_score": z_score,
            "prob_below": prob_below,
            "prob_above": prob_above,
            "pct_below": prob_below * 100.0,
            "pct_above": prob_above * 100.0
        }

    z_score = (x_val - mean) / std
    prob_below = float(stats.norm.cdf(x_val, loc=mean, scale=std))
    # Using survival function sf(x) = 1 - cdf(x) for numerical precision in extreme tails
    prob_above = float(stats.norm.sf(x_val, loc=mean, scale=std))

    return {
        "x_val": x_val,
        "z_score": float(z_score),
        "prob_below": prob_below,
        "prob_above": prob_above,
        "pct_below": prob_below * 100.0,
        "pct_above": prob_above * 100.0
    }


def calculate_interval_probability(
    x_low: float,
    x_high: float,
    mean: float,
    std: float
) -> float:
    """
    Calculates P(x_low <= X <= x_high) under N(mean, std^2):
        P(x_low <= X <= x_high) = Phi((x_high - mean)/std) - Phi((x_low - mean)/std)
    """
    if x_low > x_high:
        x_low, x_high = x_high, x_low

    if std <= 1e-9:
        return 1.0 if (x_low <= mean <= x_high) else 0.0

    cdf_high = float(stats.norm.cdf(x_high, loc=mean, scale=std))
    cdf_low = float(stats.norm.cdf(x_low, loc=mean, scale=std))
    return max(0.0, cdf_high - cdf_low)


def calculate_empirical_percentile(
    values: np.ndarray,
    x_val: float
) -> Dict[str, float]:
    """
    Calculates the empirical cumulative probability:
        Empirical P(X <= x) = Count(x_i <= x) / Total Count
    Allows direct comparison between observed real-world data and the fitted Normal model.
    """
    n = len(values)
    if n == 0:
        return {"empirical_prob_below": 0.0, "empirical_pct_below": 0.0}

    count_below = int(np.sum(values <= x_val))
    empirical_prob_below = count_below / n

    return {
        "empirical_prob_below": float(empirical_prob_below),
        "empirical_pct_below": float(empirical_prob_below * 100.0),
        "count_below": count_below,
        "count_above": n - count_below
    }


def calculate_empirical_rule_coverage(
    values: np.ndarray,
    mean: float,
    std: float
) -> Dict[str, Dict[str, Any]]:
    """
    Computes empirical coverage vs theoretical coverage under the 68-95-99.7% Rule:
    - 1 Std Dev: [mean - 1*std, mean + 1*std] -> Theoretical: 68.27%
    - 2 Std Dev: [mean - 2*std, mean + 2*std] -> Theoretical: 95.45%
    - 3 Std Dev: [mean - 3*std, mean + 3*std] -> Theoretical: 99.73%
    """
    n = len(values)
    if n == 0 or std <= 1e-9:
        return {}

    bands = {
        "1_sigma": {
            "label": "Mean ± 1σ",
            "lower": mean - 1.0 * std,
            "upper": mean + 1.0 * std,
            "theoretical_pct": 68.27
        },
        "2_sigma": {
            "label": "Mean ± 2σ",
            "lower": mean - 2.0 * std,
            "upper": mean + 2.0 * std,
            "theoretical_pct": 95.45
        },
        "3_sigma": {
            "label": "Mean ± 3σ",
            "lower": mean - 3.0 * std,
            "upper": mean + 3.0 * std,
            "theoretical_pct": 99.73
        }
    }

    for key, data in bands.items():
        count_in_band = int(np.sum((values >= data["lower"]) & (values <= data["upper"])))
        data["observed_count"] = count_in_band
        data["observed_pct"] = (count_in_band / n) * 100.0
        data["discrepancy_pct"] = data["observed_pct"] - data["theoretical_pct"]

    return bands


def assess_goodness_of_fit(
    values: np.ndarray,
    mean: float,
    std: float
) -> Dict[str, Any]:
    """
    Assesses how well the Normal distribution fits the sample network data.
    
    Tests:
    1. Kolmogorov-Smirnov Test (KS-Test):
       Compares the standardized empirical CDF against the theoretical standard normal CDF.
       H0: The sample comes from a Normal distribution.
    2. Shapiro-Wilk Test:
       Very powerful test for normality for sample sizes up to 5000.
       
    Interpretation:
    - p-value > 0.05: Fail to reject H0 (data is consistent with Normal distribution).
    - p-value <= 0.05: Reject H0 (statistically significant departure from Normal).
    
    Academic Note for Distributed Systems:
    Real-world network traffic often exhibits burstiness, Poisson arrivals, or Pareto heavy tails.
    Even when the formal hypothesis test rejects strict normality, the Normal distribution
    often serves as a practical, mathematically tractable approximation due to the
    Central Limit Theorem when traffic is aggregated across multiple flows or servers.
    """
    n = len(values)
    if n < 4 or std <= 1e-9:
        return {
            "applicable": False,
            "reason": "Sample size too small (N < 4) or variance is zero."
        }

    # Standardize data for KS test
    z_scores = (values - mean) / std

    # Kolmogorov-Smirnov test against standard normal N(0, 1)
    ks_stat, ks_pvalue = stats.kstest(z_scores, "norm")

    # Shapiro-Wilk test (applicable for N <= 5000)
    shapiro_applicable = n <= 5000
    if shapiro_applicable:
        try:
            shapiro_stat, shapiro_pvalue = stats.shapiro(values)
        except Exception:
            shapiro_applicable = False
            shapiro_stat, shapiro_pvalue = None, None
    else:
        shapiro_stat, shapiro_pvalue = None, None

    # Normal distribution fit evaluation
    alpha = 0.05
    ks_is_normal = ks_pvalue > alpha
    shapiro_is_normal = (shapiro_pvalue > alpha) if shapiro_applicable else None

    return {
        "applicable": True,
        "sample_size": n,
        "alpha": alpha,
        "ks_stat": float(ks_stat),
        "ks_pvalue": float(ks_pvalue),
        "ks_is_normal": bool(ks_is_normal),
        "shapiro_applicable": shapiro_applicable,
        "shapiro_stat": float(shapiro_stat) if shapiro_stat is not None else None,
        "shapiro_pvalue": float(shapiro_pvalue) if shapiro_pvalue is not None else None,
        "shapiro_is_normal": bool(shapiro_is_normal) if shapiro_is_normal is not None else None
    }
