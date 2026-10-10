# COLLEGE MICROPROJECT REPORT

## Project Title
**STATISTICAL MODELING OF NETWORK LOAD USING NORMAL DISTRIBUTION**

**Course**: Engineering Mathematics / Distributed Systems  
**Degree**: Bachelor of Technology (B.Tech) in Computer Science & Engineering (CSE)  
**Academic Year**: First Year (Semester 3)  
**Implementation**: Python, HTML5/CSS/JavaScript (Chart.js), Pandas, NumPy, SciPy  

---

## 1. Abstract
In modern distributed computing environments, cloud architectures, and computer networks, traffic load exhibits dynamic fluctuations driven by client requests, background jobs, and inter-node communications. Ensuring high availability and proactive capacity planning requires quantitative modeling of network telemetry. This microproject develops an interactive **Network Load Statistical Analyzer** that models network traffic using the continuous Gaussian (Normal) Distribution $\mathcal{N}(\mu, \sigma^2)$. The system calculates descriptive parameters, fits theoretical probability density functions, assesses empirical rule coverage, estimates cumulative and exceedance probabilities, and detects operational anomalies using standardized Z-scores. The application provides both a standalone, zero-server HTML5/JavaScript interactive dashboard and a verified Python mathematical backend, validated through 10 automated unit tests across normal, spike, and edge-case datasets.

---

## 2. Problem Statement
Distributed systems experience diverse network traffic patterns. Sudden load surges or link drops can degrade quality of service (QoS) or signal distributed systems anomalies (e.g., node disconnection, packet storm, heavy replication). Without statistical modeling:
1. System administrators lack an objective, quantified definition of what constitutes "normal" operating load versus an "unusual" surge.
2. Static thresholds fail to adapt when operating baselines shift.
3. Probability estimations for resource exhaustion or capacity violations cannot be made rigorously.

Therefore, an accessible, mathematically sound analyzer is needed to establish baselines, calculate probabilities, and highlight statistical deviations from network traffic logs.

---

## 3. Objectives
1. **Mathematical Parameter Estimation**: Compute sample mean, sample and population standard deviation, variance, median, IQR, skewness, and kurtosis for network load data.
2. **Normal Distribution Modeling**: Fit a Gaussian probability density curve $f(x)$ over empirical traffic histograms and evaluate alignment with the 68–95–99.7% Empirical Rule.
3. **Probability Estimation**: Enable interactive computation of cumulative probabilities $P(X \le x)$, survival probabilities $P(X > x)$, and interval probabilities $P(a \le X \le b)$ under the fitted model.
4. **Z-Score Anomaly Detection**: Normalize observations into standard scores $Z = \frac{x - \bar{x}}{s}$ and categorize load values as `Normal`, `Unusually High`, or `Unusually Low` based on user-defined thresholds.
5. **Goodness-of-Fit Evaluation**: Provide visual (Q-Q plot) and inferential (Kolmogorov-Smirnov and Shapiro-Wilk) tests to assess normality and discuss theoretical vs. practical distributed systems trade-offs.
6. **Data Processing & Validation**: Support CSV ingestion, flexible column mapping, metric unit selection, and robust cleaning for missing values and zero-variance data.

---

## 4. Methodology
The project follows a five-stage statistical and software engineering methodology:
1. **Data Ingestion & Hygiene**:
   - Ingest CSV file (synthetic cluster telemetry or real-world Kaggle logs).
   - Sanitize data by coercing non-numeric values, handling missing entries ($NaN$), and detecting duplicate records.
   - Detect and safely handle degenerate edge cases (e.g., zero variance / constant traffic).
2. **Parameter Estimation**:
   - Compute unbiased sample mean $\bar{x}$ and sample standard deviation $s$ using Bessel's correction ($N-1$ degrees of freedom).
3. **Gaussian Curve Fitting & Normalization**:
   - Map continuous Gaussian PDF: $f(x) = \frac{1}{s\sqrt{2\pi}} \exp\left(-\frac{1}{2}\left(\frac{x - \bar{x}}{s}\right)^2\right)$.
   - Standardize each observation $x_i$ to its standard normal equivalent $Z_i$.
4. **Anomaly Classification**:
   - Apply critical threshold $|Z| > k$ (standard $k = 3.0$).
   - Flag $Z > +k$ as `Unusually High` and $Z < -k$ as `Unusually Low`.
5. **Interactive Visualization & Export**:
   - Render interactive distribution plots, time-series trajectory charts with confidence bands, and Q-Q plots.
   - Provide CSV export of enriched datasets with calculated Z-scores.

---

## 5. System Architecture

```
+-------------------------------------------------------------+
|                     User Interface Layer                    |
|                         (Streamlit)                         |
|  - Data Upload & Column Mapping                             |
|  - Threshold Sliders & Unit Selectors                       |
|  - Metric Cards & Interactive Visualizations                |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                   Application Control Layer                 |
|                            (app.py)                         |
+---------------+-----------------------------+---------------+
                |                             |
                v                             v
+-------------------------------+ +---------------------------+
|      Statistical Engine       | |      Anomaly Detector     |
|    (statistics_engine.py)     | |   (anomaly_detector.py)   |
| - Descriptive Statistics      | | - Z-Score Computation     |
| - Normal PDF & CDF Modeling   | | - Threshold Logic         |
| - Empirical Rule Check        | | - Alert Categorization    |
| - Goodness-of-Fit (KS/Shapiro)| | - Edge-case Protection    |
+-------------------------------+ +---------------------------+
                |                             |
                +--------------+--------------+
                               |
                               v
+-------------------------------------------------------------+
|                     Data & Testing Layer                    |
|  - sample_network_load.csv (24-Hour Synthetic Telemetry)    |
|  - Kaggle / Custom CSV Ingestion                            |
|  - test_project.py (Automated Pytest Suite)                 |
+-------------------------------------------------------------+
```

---

## 6. Statistical Formulas

### 6.1 Sample Mean ($\bar{x}$)
$$\bar{x} = \frac{1}{N}\sum_{i=1}^N x_i$$

### 6.2 Sample Standard Deviation ($s$) vs Population Standard Deviation ($\sigma$)
- **Sample Standard Deviation ($s$, Bessel's Correction)**:
  $$s = \sqrt{\frac{1}{N - 1}\sum_{i=1}^N (x_i - \bar{x})^2}$$
  *Justification:* Network telemetry datasets represent a finite sample of a system's timeline. Bessel's correction divides by $N-1$ to eliminate negative bias in variance estimation.
- **Population Standard Deviation ($\sigma$)**:
  $$\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^N (x_i - \mu)^2}$$

### 6.3 Standard Score (Z-Score)
$$Z_i = \frac{x_i - \bar{x}}{s}$$
Represents the signed fractional count of standard deviations an observation falls above or below the mean.

### 6.4 Normal Cumulative Distribution Function (CDF)
$$P(X \le x) = \Phi(Z) = \frac{1}{\sqrt{2\pi}} \int_{-\infty}^Z e^{-t^2/2} dt = \frac{1}{2} \left[1 + \text{erf}\left(\frac{Z}{\sqrt{2}}\right)\right]$$

### 6.5 Exceedance / Survival Function
$$P(X > x) = 1 - \Phi(Z)$$

### 6.6 Empirical Rule (Three-Sigma Rule)
$$\begin{aligned}
P(\bar{x} - 1s \le X \le \bar{x} + 1s) &\approx 68.27\% \\
P(\bar{x} - 2s \le X \le \bar{x} + 2s) &\approx 95.45\% \\
P(\bar{x} - 3s \le X \le \bar{x} + 3s) &\approx 99.73\%
\end{aligned}$$

---

## 7. Dataset Description

### 7.1 Built-in Synthetic Dataset (`sample_network_load.csv`)
- **Sampling Frequency**: Every 5 minutes across a 24-hour monitoring cycle ($N = 288$ rows).
- **Domain Setting**: Node in a distributed cluster (`node-dist-cluster-01`).
- **Fields**:
  - `timestamp`: Date and time of observation (`YYYY-MM-DD HH:MM:SS`).
  - `bandwidth_mbps`: Aggregate network throughput in Megabits per second.
  - `packet_count_per_sec`: Total forwarded packets per second.
  - `cpu_utilization_percent`: Server node CPU load percentage.
  - `latency_ms`: Round-trip network response time in milliseconds.
  - `server_node_id`: Distributed node identifier.
- **Injected Operational Events**:
  - *Spike 1 (10:15 AM)*: 675.80 Mbps ($Z \approx +4.8$) — Simulates distributed database snapshot.
  - *Spike 2 (14:30 PM)*: 620.40 Mbps ($Z \approx +3.7$) — Simulates distributed ETL processing.
  - *Drop 1 (03:40 AM)*: 220.50 Mbps ($Z \approx -4.7$) — Simulates link flapping / node partition.

### 7.2 Compatibility with Real-World Datasets
The application supports arbitrary CSV files (e.g., from Kaggle, CICIDS2017, UNSW-NB15) via dynamic column selection and unit configuration.

---

## 8. Implementation Details

- **`statistics_engine.py`**:
  Contains mathematical routines written using NumPy and SciPy. Includes input verification, Bessel-corrected standard deviations, SciPy Gaussian CDF/SF functions, empirical coverage calculators, and Kolmogorov-Smirnov / Shapiro-Wilk goodness-of-fit routines.
- **`anomaly_detector.py`**:
  Calculates standard scores, applies user-selected thresholds, handles zero-variance edge cases, and tags records with alert levels (`NORMAL`, `WARNING`, `HIGH_ALERT`).
- **`app.py`**:
  Streamlit front-end featuring multi-tab navigation, Matplotlib visualization figures, probability calculator cards, interactive data tables, and CSV export.

---

## 9. Test Cases and Reliability

The system includes 10 automated unit tests implemented in `test_project.py`:

| Test Name | Focus | Input Condition | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `test_descriptive_stats_known_values` | Mathematical precision | $[10, 20, 30, 40, 50]$ | $\bar{x}=30.0$, $s=\sqrt{250}\approx 15.81$, $\sigma=\sqrt{200}\approx 14.14$ | **PASSED** |
| `test_z_score_calculation` | Standard scores | Symmetric array around 120 | $Z=0$ at mean, $Z_0 = -Z_4$ | **PASSED** |
| `test_zero_variance_constant_data` | Zero standard deviation | All values = 500.0 | $s=0.0$, $Z=0.0$, no division by zero error | **PASSED** |
| `test_theoretical_probabilities_known_cases` | Normal CDF reference points | $\mu=100, \sigma=15$ | $\Phi(0)=0.5$, $\Phi(1.96)\approx 0.975$, $1\sigma \approx 68.27\%$ | **PASSED** |
| `test_empirical_percentile` | ECDF verification | 5 points, query $x=30$ | Empirical count 3, percentile $60.0\%$ | **PASSED** |
| `test_anomaly_detection_logic` | Anomaly tagging | Data with high & low spikes | Correctly flags `Unusually High` and `Unusually Low` | **PASSED** |
| `test_validation_missing_and_dirty_data` | Data hygiene | Strings, NaNs, duplicates | Drops invalid rows, extracts valid numeric slice | **PASSED** |
| `test_validation_empty_or_missing_column` | Input safety | Empty DataFrame / bad column | Returns graceful error message without crashing | **PASSED** |
| `test_empirical_rule_coverage` | Empirical coverage | 1000 simulated normal points | Observed coverage within $\pm 4\%$ of theoretical bands | **PASSED** |
| `test_goodness_of_fit` | Hypothesis tests | Normal vs Uniform distribution | Normal: $p > 0.01$; Uniform: $p < 0.05$ (Normality rejected) | **PASSED** |

---

## 10. Results and Discussion

### 10.1 Statistical Findings on Sample Telemetry
Running the analyzer on the sample dataset yielded:
- **Valid Observations ($N$)**: 288
- **Sample Mean ($\bar{x}$)**: ~451.20 Mbps
- **Sample Standard Deviation ($s$)**: ~46.85 Mbps
- **Median**: ~449.60 Mbps
- **Empirical Rule Alignment**:
  - Within $\pm 1s$: Observed ~67.71% (Theoretical: 68.27%)
  - Within $\pm 2s$: Observed ~95.83% (Theoretical: 95.45%)
  - Within $\pm 3s$: Observed ~98.61% (Theoretical: 99.73%)
- **Identified Anomalies ($|Z| > 3.0$)**: 4 events (~1.39% of total observations):
  - 3 Unusually High events (10:15 AM, 14:30 PM, 19:20 PM)
  - 1 Unusually Low event (03:40 AM)

### 10.2 Interpretation
The close alignment between theoretical and observed percentages confirms that for macroscopic network loads with aggregated flows, the Gaussian model provides a reliable operational approximation for capacity baselines.

---

## 11. Limitations
1. **Stationarity Assumption**: The model assumes that the underlying mean $\mu$ and variance $\sigma^2$ remain constant over time. In real networks, traffic exhibits daily diurnal curves and weekly seasonality.
2. **Heavy Tails**: Real packet traffic can produce heavy-tailed bursts (Pareto or Poisson arrivals) that exceed Gaussian probability predictions at extreme quantiles.
3. **Non-Negativity Constraint**: Physical throughput cannot drop below 0 Mbps, whereas theoretical Gaussian distributions span $(-\infty, +\infty)$.
4. **Context Agnosticism**: A statistical anomaly cannot automatically determine intent (e.g., differentiating planned backups from malicious flooding).

---

## 12. Conclusion
The **Network Load Statistical Analyzer** successfully demonstrates how classical probability and statistics can be applied to real-world distributed systems monitoring. By combining descriptive statistics, continuous Normal distribution modeling, empirical rule validation, and standardized Z-score thresholding, the project delivers an end-to-end tool for baseline profiling and anomaly detection.

---

## 13. Future Enhancements
1. **Sliding-Window Dynamic Baselines**: Implement rolling statistics ($\mu_t, \sigma_t$) to adapt to circadian traffic rhythms.
2. **Alternative Distribution Support**: Integrate Log-Normal, Poisson, and Weibull distributions for comparing fit across varied traffic types.
3. **Multi-Variate Statistical Analysis**: Correlate bandwidth with CPU utilization and packet count using Mahalanobis distance.
4. **Real-Time Streaming**: Ingest live network metrics via socket or Prometheus API exporters.
