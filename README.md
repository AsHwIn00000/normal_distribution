# 🌐 Statistical Modeling of Network Load Using Normal Distribution

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Web Dashboard](https://img.shields.io/badge/Dashboard-HTML5%20%2F%20JavaScript-2563EB.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Tested](https://img.shields.io/badge/Tests-10%20Passed-brightgreen.svg)]()

> **College Microproject — 1st Year B.Tech CSE (Distributed Systems / Engineering Mathematics)**  
> An interactive statistical analyzer that models network traffic load using the **Gaussian (Normal) Distribution**, estimates cumulative and exceedance probabilities, validates empirical coverage against the 68–95–99.7% Empirical Rule, and identifies operational anomalies using standard scores (Z-scores).
>
> 🚀 **Zero-Server Standalone Webpage**: Double-click `index.html` to open the full interactive dashboard in any browser with **zero command line setup needed**!

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Quick Start (Fastest Demo)](#-quick-start-fastest-demo)
3. [Key Features](#-key-features)
4. [Project Structure](#-project-structure)
5. [Mathematical Foundations](#-mathematical-foundations)
6. [Windows Setup Instructions (VS Code)](#-windows-setup-instructions-vs-code)
7. [Using Real-World Datasets (Kaggle)](#-using-real-world-datasets-kaggle)
8. [Running Automated Tests](#-running-automated-tests)
9. [Troubleshooting Guide](#-troubleshooting-guide)
10. [Viva Voce & Interview Q&A](#-viva-voce--interview-qa)

---

## ⚡ Quick Start (Fastest Demo)

### Method 1: Just Double-Click! (Recommended)
1. Go to your project folder: `d:\College\SEMESTER_3\Maths\microproject`
2. **Double-click `index.html`**.
3. It opens immediately in Chrome, Edge, or Firefox!
   - 288 records of distributed network load are loaded and analyzed instantly.
   - All charts, probability calculators, and anomaly tables work right out of the box.

### Method 2: Launch via Python
```powershell
python open_webpage.py
```

---

## 🎯 Project Overview

In **distributed systems** (such as cloud server clusters, edge proxies, microservice meshes, and content delivery networks), monitoring traffic load is vital for capacity planning, autoscaling, and reliability engineering.

While packet generation is fundamentally bursty, the **Central Limit Theorem (CLT)** states that when thousands of independent user connections aggregate across a network interface, the aggregate load converges toward a **Normal (Gaussian) Distribution**:

$$X \sim \mathcal{N}(\mu, \sigma^2)$$

This application computes mathematical parameters, models continuous load distributions, evaluates goodness-of-fit, and flags unusually high or low load spikes using statistical **Z-scores**.

---

## ✨ Key Features

- **📊 Comprehensive Descriptive Statistics**: Calculates sample mean ($\bar{x}$), sample standard deviation ($s$ with Bessel's correction $N-1$), population standard deviation ($\sigma$, $N$), variance, median, IQR, skewness, and excess kurtosis.
- **📈 Fitted Normal Curve & Visualizations**: Overlays a theoretical probability density curve ($f(x)$) on an empirical frequency histogram with colored standard deviation bands ($\pm 1\sigma, \pm 2\sigma, \pm 3\sigma$).
- **📏 Empirical Rule Validation**: Compares actual dataset percentages within 1, 2, and 3 standard deviations against theoretical benchmarks (68.27%, 95.45%, 99.73%).
- **🧮 Interactive Probability Calculator**: Computes cumulative probability $P(X \le x)$, survival probability $P(X > x)$, and interval probability $P(a \le X \le b)$ under the fitted model, alongside empirical percentiles.
- **🚨 Z-Score Anomaly Detection**: Configurable threshold (default $|Z| > 3.0$) categorizing observations into `Normal`, `Unusually High` (e.g., database backups, heavy query burst, traffic surges), and `Unusually Low` (e.g., link flaps, failovers, node partitioning).
- **🔬 Goodness-of-Fit Testing**: Quantile-Quantile (Q-Q) plots comparing observed quantiles against theoretical Gaussian quantiles to examine normality assumptions.
- **🛡️ Robust Error & Edge-Case Handling**: Cleans missing values (`NaN`), duplicate entries, non-numeric strings, and safely handles zero standard deviation (constant load datasets) without division by zero.
- **📥 CSV Export**: Exports analyzed datasets enriched with calculated Z-scores and alert levels.
- **🎓 Embedded Viva Voce Guide**: Formula cheat-sheet and 8 core oral examination questions embedded directly inside the dashboard.

---

## 📂 Project Structure

```text
microproject/
├── index.html                 # Complete standalone webpage (double-click to open!)
├── open_webpage.py            # Python one-liner to launch index.html in default browser
├── build_index_html.py        # Generator script assembling index.html with sample data
├── statistics_engine.py       # Pure Python statistical engine, Normal CDF/PDF, hypothesis tests
├── anomaly_detector.py        # Z-score classification, thresholding, and alert logic
├── generate_sample_data.py    # Generator for realistic 24-hr distributed cluster traffic
├── sample_network_load.csv    # Synthetic dataset (288 observations, 5-minute intervals)
├── test_project.py            # Automated pytest test suite (10 unit tests)
├── requirements.txt           # Python dependencies
├── PROJECT_REPORT.md          # College project report outline
└── README.md                  # Complete project documentation & viva guide
```

---

## 📐 Mathematical Foundations

### 1. Sample vs. Population Standard Deviation
- **Sample Standard Deviation ($s$)** — *Used by default in this project*:
  $$s = \sqrt{\frac{1}{N - 1}\sum_{i=1}^N (x_i - \bar{x})^2}$$
  *Why:* Traffic datasets represent a temporal **sample** of network operations. Dividing by $N - 1$ (**Bessel's correction**) compensates for sample bias and provides an unbiased estimator of true variance.
- **Population Standard Deviation ($\sigma$)**:
  $$\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^N (x_i - \mu)^2}$$
  Used only when analyzing 100% of all traffic transmitted in a network's entire lifetime.

### 2. Normal Probability Density Function (PDF)
$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left( -\frac{1}{2}\left(\frac{x - \mu}{\sigma}\right)^2 \right)$$

### 3. Z-Score (Standard Score)
$$Z = \frac{x - \bar{x}}{s}$$
Measures the number of standard deviations observation $x$ lies away from the baseline mean $\bar{x}$.

### 4. Cumulative Distribution Function (CDF)
$$P(X \le x) = \Phi(Z) = \frac{1}{2} \left[ 1 + \text{erf}\left( \frac{Z}{\sqrt{2}} \right) \right]$$
Calculated with high precision using the error function $\text{erf}(x)$. Exceedance probability $P(X > x) = 1 - \Phi(Z)$.

### 5. Empirical Rule (Three-Sigma Rule)
- $[\mu - 1\sigma, \mu + 1\sigma] \approx 68.27\%$ of observations
- $[\mu - 2\sigma, \mu + 2\sigma] \approx 95.45\%$ of observations
- $[\mu - 3\sigma, \mu + 3\sigma] \approx 99.73\%$ of observations

---

## 💻 Windows Setup Instructions (VS Code)

Follow these exact steps in **Visual Studio Code** on Windows:

### Step 1: Open the Project Folder
1. Launch VS Code.
2. Go to **File** $\to$ **Open Folder...**
3. Select `d:\College\SEMESTER_3\Maths\microproject`.

### Step 2: Open PowerShell Terminal
In VS Code, press ``Ctrl + ` `` (Backtick) or go to **Terminal** $\to$ **New Terminal**.

### Step 3: Run the Automated Unit Tests
To show your professor that the underlying Python mathematical code is 100% verified:
```powershell
pytest test_project.py -v
```
*(Expected output: `10 passed in 2.13s`)*

### Step 4: Open the Web Dashboard
Either:
- Simply double-click `index.html` in your file explorer, OR
- Run in terminal:
  ```powershell
  python open_webpage.py
  ```

---

## 📁 Using Real-World Datasets (Kaggle)

You can download real network traffic datasets from Kaggle (e.g., *UNSW-NB15*, *CICIDS2017*, *Internet Traffic Archive*, or *Cloud Network Metrics*) and analyze them:

1. In the header of `index.html`, click **"📂 Upload Custom CSV"**.
2. Select your downloaded `.csv` file.
3. Use the dropdown controls to map:
   - **Target Load Column**: Choose your numerical metric (e.g., `bandwidth`, `throughput`, `packet_count`).
   - **Timestamp Column**: Choose your timestamp column.
   - **Metric Unit**: Choose `Mbps`, `Packets / sec`, `KB / s`, etc.
4. The dashboard will instantly recalculate all statistics, update the charts, and flag anomalies!

---

## 🧪 Running Automated Tests

The project includes 10 rigorous unit tests in `test_project.py`:
- `test_descriptive_stats_known_values`: Mathematical verification of mean, sample std, population std, median, min, max.
- `test_z_score_calculation`: Verification of standard score normalization and symmetry.
- `test_zero_variance_constant_data`: Safe handling of zero standard deviation without division by zero.
- `test_theoretical_probabilities_known_cases`: Validating $\Phi(0) = 0.5$, $\Phi(1.96) \approx 0.975$, and 68-95-99.7% intervals.
- `test_empirical_percentile`: Verifying ECDF calculation against exact counts.
- `test_anomaly_detection_logic`: Classification into `Normal`, `Unusually High`, and `Unusually Low`.
- `test_validation_missing_and_dirty_data`: Automatic cleaning of strings, NaNs, and duplicate detection.
- `test_validation_empty_or_missing_column`: Graceful error handling for missing inputs.
- `test_empirical_rule_coverage`: Validation of empirical vs theoretical band coverage.
- `test_goodness_of_fit`: KS-test and Shapiro-Wilk test on normal vs non-normal datasets.

Run tests:
```powershell
pytest test_project.py -v
```

---

## 🛠️ Troubleshooting Guide

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| Charts do not appear when opening `index.html` | Internet disconnected during first load | Ensure you are connected to internet on initial load so Chart.js CDN loads, or keep Chart.js cached. |
| CSV upload does not show data | CSV has missing headers or corrupted encoding | Make sure the CSV file has a header row with column names and UTF-8 encoding. |
| `pytest` command not recognized | Virtual environment not activated | Activate virtual environment: `.\venv\Scripts\activate`. |

---

## 🎓 Viva Voce & Interview Q&A

**1. What is the difference between sample variance and population variance?**  
> *Sample variance divides by $(N - 1)$ (Bessel's correction) to avoid underestimating variability when working with sample data. Population variance divides by $N$ and is only used when the data represents the complete population.*

**2. What does a Z-score of +3.5 mean in network engineering?**  
> *It means the observed network load is 3.5 standard deviations above the average traffic baseline. Under a standard Normal distribution, such a value occurs less than 0.1% of the time, making it an extreme statistical outlier.*

**3. Does a statistical anomaly imply a malicious cyberattack?**  
> *No. In distributed systems, high load spikes frequently stem from benign operational events such as automated database snapshots, distributed MapReduce tasks, or cluster node resynchronizations. Statistical anomalies flag points of interest for human or automated review.*

**4. Why is network traffic only approximately Gaussian?**  
> *Real network packet arrivals often follow a Poisson process or heavy-tailed Pareto distribution. Additionally, network traffic cannot be negative ($x \ge 0$). However, when thousands of flows aggregate together, the Central Limit Theorem causes the total load to approximate a Normal distribution.*

**5. How do you evaluate goodness-of-fit?**  
> *Using a Quantile-Quantile (Q-Q) plot (checking if points lie along the 45-degree theoretical reference line) and evaluating sample skewness and kurtosis.*

---
*Created for College Microproject &bull; Free, fast, and locally executable.*
