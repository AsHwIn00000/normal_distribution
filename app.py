"""
app.py
======
Network Load Statistical Analyzer
Statistical Modeling of Network Load Using Normal Distribution

Industry Focus: Distributed Systems
Integrated Course Outcomes: CO3, CO4, CO5

Architecture:
- Streamlit modern academic analytics dashboard
- Separation of concerns: pure stats engine (statistics_engine.py), anomaly detector (anomaly_detector.py)
- Three primary sections:
    1. Overview & Distribution
    2. Anomaly Detection
    3. Detailed Analysis
- Expandable Educational & Viva Voce preparation section
- Dual CSV download support (full analyzed dataset & anomaly report)
- Dynamic engineering conclusions & methodology documentation
"""

import io
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

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


# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Network Load Statistical Analyzer",
    page_icon="favicon.svg" if os.path.exists("favicon.svg") else "📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design System CSS (Modern Academic Analytics Theme)
st.markdown("""
<style>
    /* Font & Global Reset */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0F172A;
    }
    
    /* Main Background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Premium Header Container */
    .header-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 60%, #1D4ED8 100%);
        color: #FFFFFF;
        padding: 26px 32px;
        border-radius: 14px;
        box-shadow: 0 4px 16px -2px rgba(30, 58, 138, 0.18);
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 1.95rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
        color: #FFFFFF;
    }
    .header-subtitle {
        font-size: 1.05rem;
        font-weight: 500;
        color: #BFDBFE;
        margin-bottom: 8px;
    }
    .header-description {
        font-size: 0.92rem;
        color: #E2E8F0;
        max-width: 880px;
        line-height: 1.45;
        margin-bottom: 14px;
    }
    .badge-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 6px;
    }
    .header-badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        border-radius: 9999px;
        background: rgba(255, 255, 255, 0.18);
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(4px);
    }

    /* Quick Dataset Action Bar */
    .action-bar-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }
    .dataset-info-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E40AF;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        text-align: left;
        position: relative;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px -2px rgba(0, 0, 0, 0.07);
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    .metric-caption {
        font-size: 0.78rem;
        color: #64748B;
        line-height: 1.35;
    }
    
    /* Content Card */
    .content-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    
    /* Callout & Note Boxes */
    .note-box {
        background: #F0F9FF;
        border-left: 4px solid #0284C7;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #0369A1;
        margin-top: 10px;
        margin-bottom: 14px;
        line-height: 1.45;
    }
    .warning-box {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #92400E;
        margin-top: 10px;
        margin-bottom: 14px;
        line-height: 1.45;
    }
    .success-box {
        background: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #047857;
        margin-top: 10px;
        margin-bottom: 14px;
        line-height: 1.45;
    }

    /* Visual indicator bar for probability calculator */
    .visual-bar-container {
        margin-top: 14px;
        background: #F1F5F9;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #E2E8F0;
    }

    /* Parameter Grid */
    .stat-pill {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .stat-pill-label {
        font-size: 0.74rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .stat-pill-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar & Session State: Dataset Ingestion & Controls
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Dataset & Variables")

default_sample_path = "sample_network_load.csv"

# Initialize session state for dataset persistence
if "dataset_mode" not in st.session_state:
    st.session_state.dataset_mode = "sample"
if "custom_csv_df" not in st.session_state:
    st.session_state.custom_csv_df = None
if "custom_csv_name" not in st.session_state:
    st.session_state.custom_csv_name = ""

# Sidebar dataset mode radio
sidebar_source_choice = st.sidebar.radio(
    "Data Source:",
    ["Use Existing Sample Dataset (sample_network_load.csv)", "Upload Custom CSV File"],
    index=0 if st.session_state.dataset_mode == "sample" else 1
)

if "Existing Sample" in sidebar_source_choice:
    st.session_state.dataset_mode = "sample"
else:
    st.session_state.dataset_mode = "upload"

# File uploader in sidebar
if st.session_state.dataset_mode == "upload":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Network Traffic CSV",
        type=["csv"],
        help="Upload any real or synthetic CSV dataset containing network load metrics."
    )
    if uploaded_file is not None:
        try:
            st.session_state.custom_csv_df = pd.read_csv(uploaded_file)
            st.session_state.custom_csv_name = uploaded_file.name
            st.sidebar.success(f"Loaded '{uploaded_file.name}' ({len(st.session_state.custom_csv_df)} rows)")
        except Exception as e:
            st.sidebar.error(f"Failed to parse CSV: {e}")

# Resolve active DataFrame
df_raw = None
active_dataset_name = ""

if st.session_state.dataset_mode == "sample":
    if os.path.exists(default_sample_path):
        try:
            df_raw = pd.read_csv(default_sample_path)
            active_dataset_name = "sample_network_load.csv"
        except Exception as e:
            st.sidebar.error(f"Error reading sample dataset: {e}")
    else:
        st.sidebar.error(f"Default dataset '{default_sample_path}' not found.")
else:
    if st.session_state.custom_csv_df is not None:
        df_raw = st.session_state.custom_csv_df
        active_dataset_name = st.session_state.custom_csv_name
    else:
        st.sidebar.info("Awaiting custom CSV upload...")

# Reset to Sample Data button in sidebar
if st.sidebar.button("🔄 Reset to Default Sample Data"):
    st.session_state.dataset_mode = "sample"
    st.session_state.custom_csv_df = None
    st.session_state.custom_csv_name = ""
    st.rerun()

if df_raw is None or df_raw.empty:
    st.info("Please select or upload a valid network traffic CSV dataset to begin analysis.")
    st.stop()

all_columns = list(df_raw.columns)
numeric_cols = [c for c in all_columns if pd.to_numeric(df_raw[c], errors="coerce").notna().sum() > 0]

if not numeric_cols:
    st.error("❌ The loaded dataset contains no numeric columns suitable for statistical modeling.")
    st.stop()

# Primary Variable Selector
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Variable Selection")

# Priority mapping: bandwidth_mbps as default primary
var_options = []
if "bandwidth_mbps" in all_columns:
    var_options.append("bandwidth_mbps (Primary Network Load)")
if "packet_count_per_sec" in all_columns:
    var_options.append("packet_count_per_sec (Packet Count)")
if "latency_ms" in all_columns:
    var_options.append("latency_ms (Round-Trip Latency)")
var_options.append("Other Numerical Column...")

chosen_var_mode = st.sidebar.radio("Analysis Variable:", var_options, index=0)

if "bandwidth_mbps" in chosen_var_mode:
    selected_load_col = "bandwidth_mbps"
    default_unit = "Mbps"
elif "packet_count_per_sec" in chosen_var_mode:
    selected_load_col = "packet_count_per_sec"
    default_unit = "Packets/s"
elif "latency_ms" in chosen_var_mode:
    selected_load_col = "latency_ms"
    default_unit = "ms"
else:
    selected_load_col = st.sidebar.selectbox("Select Numerical Column:", options=numeric_cols, index=0)
    default_unit = "units"

# Unit Selector
unit_presets = [default_unit, "Mbps", "Gbps", "Packets/s", "KB/s", "MB/s", "% Utilization", "ms", "Req/s", "Custom..."]
unit_presets = list(dict.fromkeys(unit_presets))
chosen_unit_str = st.sidebar.selectbox("Measurement Unit:", unit_presets, index=0)
if chosen_unit_str == "Custom...":
    load_unit = st.sidebar.text_input("Enter custom unit name:", value="units")
else:
    load_unit = chosen_unit_str

# Timestamp column selection
timestamp_candidates = ["None (Observation Sequence)"] + all_columns
default_time_idx = 0
for i, col in enumerate(all_columns):
    c_lower = col.lower()
    if any(k in c_lower for k in ["time", "date", "ts", "timestamp"]):
        default_time_idx = i + 1
        break

selected_time_col = st.sidebar.selectbox(
    "Timestamp Column (Optional):",
    timestamp_candidates,
    index=default_time_idx,
    help="Select the column representing time for sequence plotting."
)
timestamp_column = None if selected_time_col == "None (Observation Sequence)" else selected_time_col

# Node Filter if multi-node data exists (e.g. server_node_id)
node_column = None
for c in all_columns:
    if "node" in c.lower() or "server" in c.lower() or "host" in c.lower():
        node_column = c
        break

filtered_df = df_raw.copy()
selected_node = "All Nodes (Cluster Aggregate)"
if node_column and df_raw[node_column].nunique() > 1:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🖥️ Distributed Node Filtering")
    unique_nodes = ["All Nodes (Cluster Aggregate)"] + list(df_raw[node_column].dropna().unique())
    selected_node = st.sidebar.selectbox(f"Filter by {node_column}:", unique_nodes, index=0)
    if selected_node != "All Nodes (Cluster Aggregate)":
        filtered_df = filtered_df[filtered_df[node_column] == selected_node]
        st.sidebar.caption(f"Filtered to {len(filtered_df)} records for {selected_node}.")

# Statistical parameters in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📐 Statistical Settings")
z_threshold = st.sidebar.slider(
    "Z-Score Threshold (|Z|):",
    min_value=1.5,
    max_value=4.0,
    value=3.0,
    step=0.1,
    help="Controls how many standard deviations from the mean an observation must be to be flagged. Default: 3.0 (Three-Sigma rule)."
)

std_method_choice = st.sidebar.selectbox(
    "Standard Deviation Method:",
    ["Sample Std Dev (s, Bessel's N-1) [Default]", "Population Std Dev (σ, N)"],
    index=0,
    help="Use Sample (N-1) when treating observations as a sample of traffic. Use Population (N) only if analyzing the complete lifetime population."
)
ddof_value = 1 if "Sample" in std_method_choice else 0


# ---------------------------------------------------------
# Data Validation & Statistical Computation
# ---------------------------------------------------------
val_res = validate_network_data(filtered_df, selected_load_col, timestamp_column=timestamp_column)

if not val_res["is_valid"]:
    st.error(f"❌ Data Validation Error: {val_res['error_message']}")
    st.stop()

clean_df = val_res["clean_df"]
load_values = val_res["load_values"]
total_rows = val_res["total_rows"]
valid_n = val_res["valid_observations"]
missing_n = val_res["missing_count"]
duplicate_n = val_res["duplicate_count"]
is_constant = val_res["is_constant"]

# Descriptive stats
stats_dict = calculate_descriptive_stats(load_values, ddof=ddof_value)
mean_val = stats_dict["mean"]
sample_std_val = stats_dict["sample_std"]
pop_std_val = stats_dict["population_std"]
active_std_val = stats_dict["std"]
sample_var_val = stats_dict["sample_var"]
pop_var_val = stats_dict["population_var"]
active_var_val = stats_dict["variance"]
min_val = stats_dict["min"]
max_val = stats_dict["max"]
median_val = stats_dict["median"]
iqr_val = stats_dict["iqr"]
skewness_val = stats_dict["skewness"]
kurtosis_val = stats_dict["kurtosis"]

# Anomaly Detection
anomaly_res = detect_network_anomalies(
    clean_df,
    load_column=selected_load_col,
    z_threshold=z_threshold,
    timestamp_column=timestamp_column,
    mean=mean_val,
    std=active_std_val,
    ddof=ddof_value
)

enriched_df = anomaly_res["enriched_df"]
anomalies_df = anomaly_res["anomalies_df"]
total_anomalies = anomaly_res["total_anomalies"]
high_anomalies = anomaly_res["high_anomalies"]
low_anomalies = anomaly_res["low_anomalies"]
anomaly_rate = anomaly_res["anomaly_rate_pct"]


# ---------------------------------------------------------
# Section 3: Main Header
# ---------------------------------------------------------
st.markdown(f"""
<div class="header-card">
    <div class="header-title">Network Load Statistical Analyzer</div>
    <div class="header-subtitle">Statistical Modeling of Network Load Using Normal Distribution</div>
    <div class="header-description">
        Analyze network traffic patterns, understand statistical variation, and identify unusual load conditions.
        Designed for distributed systems capacity planning, baseline modeling, and operational reliability.
    </div>
    <div class="badge-container">
        <span class="header-badge">College Microproject</span>
        <span class="header-badge">Distributed Systems</span>
        <span class="header-badge">CO3, CO4, CO5</span>
        <span class="header-badge">Dataset: {active_dataset_name}</span>
        <span class="header-badge">Variable: {selected_load_col} ({load_unit})</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Action Bar: Direct File Upload & Reset accessible right under the header
with st.container():
    act_col1, act_col2, act_col3 = st.columns([4, 2, 2])
    with act_col1:
        st.markdown(f"""
        <div style="font-size:0.86rem; color:#475569; padding-top:6px;">
            <b>Active Dataset:</b> <span style="color:#1E40AF; font-weight:600;">{active_dataset_name}</span>
            &bull; Observations: <b>{valid_n:,}</b> valid
            {f'&bull; <span style="color:#DC2626;">Cleaned: {missing_n} missing</span>' if missing_n > 0 else '&bull; Zero missing values'}
        </div>
        """, unsafe_allow_html=True)
    with act_col2:
        if st.session_state.dataset_mode == "sample":
            if st.button("📤 Upload Custom CSV", use_container_width=True):
                st.session_state.dataset_mode = "upload"
                st.rerun()
        else:
            if st.button("📁 Switch to Sample CSV", use_container_width=True):
                st.session_state.dataset_mode = "sample"
                st.rerun()
    with act_col3:
        if st.button("🔄 Reset to Default Data", use_container_width=True):
            st.session_state.dataset_mode = "sample"
            st.session_state.custom_csv_df = None
            st.session_state.custom_csv_name = ""
            st.rerun()


# ---------------------------------------------------------
# Section 5: Top Four Prominent Metric Cards
# ---------------------------------------------------------
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Card 1: Total Observations</div>
        <div class="metric-val">{valid_n:,}</div>
        <div class="metric-caption">
            An observation is one recorded measurement in the dataset.<br>
            <span style="color:#0284C7; font-weight:500;">Valid: {valid_n} | Missing: {missing_n} | Duplicates: {duplicate_n}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Card 2: Mean Network Load</div>
        <div class="metric-val">{mean_val:.2f} <span style="font-size:0.95rem; font-weight:500;">{load_unit}</span></div>
        <div class="metric-caption">
            <b>Formula:</b> Mean = Sum of observations / N.<br>
            The mean represents the average network load in the selected dataset.
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    std_label = "Sample Std Dev (s)" if ddof_value == 1 else "Pop Std Dev (σ)"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Card 3: Standard Deviation</div>
        <div class="metric-val">{active_std_val:.2f} <span style="font-size:0.95rem; font-weight:500;">{load_unit}</span></div>
        <div class="metric-caption">
            {std_label} (Variance: {active_var_val:.1f} {load_unit}²).<br>
            Standard deviation measures how widely the measurements vary around their mean.
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    anom_color = "#DC2626" if total_anomalies > 0 else "#16A34A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Card 4: Flagged Anomalies (|Z| &gt; {z_threshold:.1f})</div>
        <div class="metric-val" style="color: {anom_color};">{total_anomalies} <span style="font-size:1rem; color:#64748B;">({anomaly_rate:.1f}%)</span></div>
        <div class="metric-caption">
            {high_anomalies} High | {low_anomalies} Low.<br>
            Measurements differing substantially from the mean; not automatically a cyberattack or system failure.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# Dataset Preview & Data Hygiene Details (Collapsible)
# ---------------------------------------------------------
with st.expander("🔍 Dataset Preview & Data Hygiene Inspection", expanded=False):
    st.markdown(f"**Loaded File:** `{active_dataset_name}` | **Total Rows:** `{total_rows}` | **Valid Observations:** `{valid_n}` | **Cleaned Missing:** `{missing_n}` | **Duplicates:** `{duplicate_n}`")
    st.dataframe(clean_df.head(10), use_container_width=True)
    if missing_n > 0:
        st.info(f"Cleaned {missing_n} missing / non-numeric entries to avoid statistical distortion.")
    if is_constant:
        st.error("Zero Standard Deviation: All observations are identical in the selected column.")


# ---------------------------------------------------------
# Section 6: Simplified 3 Primary Sections Navigation
# ---------------------------------------------------------
section_tabs = st.tabs([
    "1. Overview & Distribution",
    "2. Anomaly Detection",
    "3. Detailed Analysis"
])


# =========================================================
# SECTION 1: OVERVIEW & DISTRIBUTION
# =========================================================
with section_tabs[0]:
    st.markdown("### 1. Overview & Distribution Analysis")
    st.markdown(
        "Model the continuous distribution of network load using the Gaussian (Normal) curve "
        "and compare empirical observations with theoretical probability density."
    )

    col_graph, col_calc = st.columns([3, 2])

    with col_graph:
        # Scale mode selector
        scale_mode = st.radio(
            "Graph Scale Mode:",
            ["Probability Density Scale (Theoretical PDF f(x))", "Frequency Count Scale (Scaled Normal Curve)"],
            horizontal=True,
            help="Choose whether to plot normalized probability density (area=1.0) or discrete observation counts scaled by bin width."
        )

        use_density = "Probability Density" in scale_mode

        fig1, ax1 = plt.subplots(figsize=(8.8, 5.3), dpi=125)
        
        # Calculate optimal bin count using Freedman-Diaconis or Sturges rule
        n_bins = min(35, max(10, int(np.sqrt(valid_n))))
        
        counts, bin_edges, patches = ax1.hist(
            load_values,
            bins=n_bins,
            density=use_density,
            alpha=0.50,
            color="#3B82F6",
            edgecolor="#1D4ED8",
            linewidth=1.0,
            label="Observed Traffic (Histogram Density)" if use_density else "Observed Traffic (Bin Frequency)"
        )

        bin_width = bin_edges[1] - bin_edges[0] if len(bin_edges) > 1 else 1.0

        # Plot fitted continuous Normal curve
        if active_std_val > 1e-9:
            x_min = min(float(np.min(load_values)), mean_val - 3.8 * active_std_val)
            x_max = max(float(np.max(load_values)), mean_val + 3.8 * active_std_val)
            x_axis = np.linspace(x_min, x_max, 450)
            normal_pdf = stats.norm.pdf(x_axis, loc=mean_val, scale=active_std_val)
            
            # Scale curve appropriately if count scale selected
            y_curve = normal_pdf if use_density else normal_pdf * valid_n * bin_width
            
            ax1.plot(
                x_axis,
                y_curve,
                color="#DC2626",
                linewidth=2.4,
                label=f"Fitted Normal N(μ={mean_val:.1f}, σ={active_std_val:.1f})"
            )

            # Mean vertical line
            ax1.axvline(
                mean_val,
                color="#0F172A",
                linestyle="-",
                linewidth=1.8,
                label=f"Mean (μ = {mean_val:.1f} {load_unit})"
            )

            # Standard deviation markers (+/- 1s, 2s, 3s)
            ax1.axvline(mean_val - active_std_val, color="#10B981", linestyle="--", linewidth=1.2)
            ax1.axvline(mean_val + active_std_val, color="#10B981", linestyle="--", linewidth=1.2, label="±1σ (68.3% band)")

            ax1.axvline(mean_val - 2 * active_std_val, color="#F59E0B", linestyle="--", linewidth=1.2)
            ax1.axvline(mean_val + 2 * active_std_val, color="#F59E0B", linestyle="--", linewidth=1.2, label="±2σ (95.5% band)")

            ax1.axvline(mean_val - 3 * active_std_val, color="#EF4444", linestyle=":", linewidth=1.3)
            ax1.axvline(mean_val + 3 * active_std_val, color="#EF4444", linestyle=":", linewidth=1.3, label="±3σ (99.7% band)")

            # Shaded central 1-sigma zone
            x_1s = np.linspace(mean_val - active_std_val, mean_val + active_std_val, 150)
            y_1s = stats.norm.pdf(x_1s, mean_val, active_std_val) if use_density else stats.norm.pdf(x_1s, mean_val, active_std_val) * valid_n * bin_width
            ax1.fill_between(x_1s, y_1s, color="#10B981", alpha=0.12)

        ax1.set_title(f"Network Load Distribution & Fitted Normal Model ({selected_load_col})", fontsize=11, fontweight="bold", pad=12)
        ax1.set_xlabel(f"Network Load ({load_unit})", fontsize=10)
        ax1.set_ylabel("Probability Density f(x)" if use_density else "Observation Count (Frequency)", fontsize=10)
        ax1.grid(True, linestyle=":", alpha=0.55)
        ax1.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
        fig1.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    with col_calc:
        # Section 8: Interactive Probability Calculator
        st.markdown("#### 🧮 Probability Calculator")
        st.markdown(
            "Enter a network-load value to calculate its theoretical probability under the fitted Normal model "
            "and compare it with the observed empirical percentile."
        )

        default_input = float(round(mean_val + active_std_val, 1))
        user_x = st.number_input(
            f"Enter Load Value ({load_unit}):",
            value=default_input,
            step=1.0,
            format="%.2f",
            key="calc_user_input"
        )

        prob_res = calculate_theoretical_probability(user_x, mean_val, active_std_val)
        emp_res = calculate_empirical_percentile(load_values, user_x)

        z_calc = prob_res["z_score"]
        p_below = prob_res["prob_below"]
        p_above = prob_res["prob_above"]
        emp_pct = emp_res["empirical_pct_below"]

        if active_std_val > 1e-9:
            st.markdown(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin-top: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:0.9rem; margin-bottom: 6px;">
                    <b>Standardized Z-Score:</b> <code style="font-size:1rem; color:#1E40AF;">Z = {z_calc:.3f}</code>
                </div>
                <div style="font-size:0.88rem; margin-bottom: 5px;">
                    <b>Theoretical P(X ≤ {user_x:.1f}):</b> <code>{p_below:.4f} ({p_below * 100:.2f}%)</code>
                </div>
                <div style="font-size:0.88rem; margin-bottom: 5px;">
                    <b>Theoretical Exceedance P(X &gt; {user_x:.1f}):</b> <code>{p_above:.4f} ({p_above * 100:.2f}%)</code>
                </div>
                <hr style="border:none; border-top: 1px solid #E2E8F0; margin: 8px 0;">
                <div style="font-size:0.88rem; color:#0369A1;">
                    <b>Observed Empirical Percentile:</b> <code>{emp_pct:.2f}%</code> ({emp_res['count_below']} of {valid_n} samples)
                </div>
                <div style="font-size:0.75rem; color:#64748B; margin-top: 3px;">
                    Model Discrepancy (Residual): {abs(p_below * 100 - emp_pct):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Visual position indicator
            clamped_z = max(-3.5, min(3.5, z_calc))
            norm_pos = ((clamped_z + 3.5) / 7.0) * 100
            st.markdown(f"""
            <div class="visual-bar-container">
                <div style="font-size:0.75rem; font-weight:600; color:#64748B; margin-bottom:4px; display:flex; justify-content:space-between;">
                    <span>-3σ</span>
                    <span>-2σ</span>
                    <span>-1σ</span>
                    <span style="color:#0F172A;">Mean (μ)</span>
                    <span>+1σ</span>
                    <span>+2σ</span>
                    <span>+3σ</span>
                </div>
                <div style="position:relative; height:10px; background:#CBD5E1; border-radius:5px; width:100%;">
                    <div style="position:absolute; left:{norm_pos}%; top:-4px; width:8px; height:18px; background:#DC2626; border-radius:3px; transform:translateX(-50%);"></div>
                </div>
                <div style="font-size:0.75rem; color:#64748B; margin-top:6px; text-align:center;">
                    Entered input ({user_x:.1f} {load_unit}) is <b>{abs(z_calc):.2f} std devs</b> {'above' if z_calc >= 0 else 'below'} mean.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Standard deviation is zero (all values in dataset are identical). Theoretical Normal curve collapses to a single point at the mean.")

    # Section 7.B: Statistical Summary
    st.markdown("---")
    st.markdown("#### 📋 Statistical Summary Grid")
    
    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Valid Observations (N)</div>
            <div class="stat-pill-value">{valid_n:,}</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-label">Sample Mean (x̄)</div>
            <div class="stat-pill-value">{mean_val:.2f} {load_unit}</div>
        </div>
        """, unsafe_allow_html=True)
    with summary_cols[1]:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Sample Std Dev (s, N-1)</div>
            <div class="stat-pill-value">{sample_std_val:.2f} {load_unit}</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-label">Population Std Dev (σ, N)</div>
            <div class="stat-pill-value">{pop_std_val:.2f} {load_unit}</div>
        </div>
        """, unsafe_allow_html=True)
    with summary_cols[2]:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Sample Variance (s²)</div>
            <div class="stat-pill-value">{sample_var_val:.2f} {load_unit}²</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-label">Median (Q2)</div>
            <div class="stat-pill-value">{median_val:.2f} {load_unit}</div>
        </div>
        """, unsafe_allow_html=True)
    with summary_cols[3]:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Minimum Observed</div>
            <div class="stat-pill-value">{min_val:.2f} {load_unit}</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-label">Maximum Observed</div>
            <div class="stat-pill-value">{max_val:.2f} {load_unit}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="note-box">
        <b>Distinction between Sample and Population Standard Deviation:</b><br>
        • <b>Sample Standard Deviation (s, N-1):</b> Uses Bessel's correction (dividing by N - 1 = {valid_n - 1}) to eliminate negative bias when working with sample datasets.<br>
        • <b>Population Standard Deviation (σ, N):</b> Divides by N = {valid_n}; used only if analyzing all historical traffic that will ever occur.
    </div>
    """, unsafe_allow_html=True)



# =========================================================
# SECTION 2: ANOMALY DETECTION
# =========================================================
with section_tabs[1]:
    st.markdown("### 2. Anomaly Detection & Statistical Deviation")
    st.markdown(
        "Identify operational measurements that deviate substantially from the baseline using standard scores (Z-scores). "
        "A statistical anomaly represents an outlier, not necessarily a cyberattack or system failure."
    )

    # A. Threshold control
    col_t1, col_t2 = st.columns([2, 3])
    with col_t1:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px;">
            <div style="font-size:0.85rem; font-weight:600; color:#64748B;">CONFIGURED THRESHOLD</div>
            <div style="font-size:1.8rem; font-weight:700; color:#1E40AF;">|Z| &gt; {z_threshold:.1f}</div>
            <div style="font-size:0.8rem; color:#64748B; margin-top:4px;">
                Upper Boundary: <b>{(mean_val + z_threshold * active_std_val):.2f} {load_unit}</b><br>
                Lower Boundary: <b>{(mean_val - z_threshold * active_std_val):.2f} {load_unit}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
        <div class="warning-box" style="margin-top:0;">
            <b>💡 Operational Context for Distributed Systems:</b><br>
            Formula: <code>Z = (Observed Load - Mean) / Standard Deviation</code>.<br>
            • <b>Unusually High (Z &gt; +{z_threshold:.1f}):</b> Large distributed backups, cluster ETL sync, database replication, or heavy user traffic surges.<br>
            • <b>Unusually Low (Z &lt; -{z_threshold:.1f}):</b> Routing shifts, transient link flaps, server maintenance windows, or off-peak idle periods.
        </div>
        """, unsafe_allow_html=True)

    # C. Anomaly Summary Cards
    st.markdown("#### Anomaly Summary")
    anom_c1, anom_c2, anom_c3, anom_c4 = st.columns(4)
    anom_c1.metric("Total Flagged", f"{total_anomalies}", f"{anomaly_rate:.1f}% of records")
    anom_c2.metric("Unusually High (Spikes)", f"{high_anomalies}", f"Z > +{z_threshold:.1f}")
    anom_c3.metric("Unusually Low (Dips)", f"{low_anomalies}", f"Z < -{z_threshold:.1f}")
    anom_c4.metric("Normal Operating Records", f"{valid_n - total_anomalies}", f"{(100 - anomaly_rate):.1f}%")

    # D. Anomaly Table with Sorting & Filtering
    st.markdown("---")
    st.markdown("#### Anomaly Observation Table")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_mode = st.selectbox(
            "Filter Observations:",
            ["Flagged Anomalies Only", "Unusually High Only (Spikes)", "Unusually Low Only (Dips)", "All Records (with Z-scores)"],
            index=0
        )
    with filter_col2:
        sort_mode = st.selectbox(
            "Sort Table By:",
            ["Original Sequence Index (#)", "Most Extreme Z-Score (|Z| descending)", "Highest Measured Load First", "Lowest Measured Load First"],
            index=0
        )

    # Select columns to display
    display_cols = ["observation_index"]
    if timestamp_column and timestamp_column in enriched_df.columns:
        display_cols.append(timestamp_column)
    display_cols.extend([selected_load_col, "z_score", "anomaly_status", "alert_level"])

    # Filter dataframe
    if filter_mode == "Flagged Anomalies Only":
        table_view = enriched_df[enriched_df["is_anomaly"]][display_cols].copy()
    elif filter_mode == "Unusually High Only (Spikes)":
        table_view = enriched_df[enriched_df["anomaly_status"] == "Unusually High"][display_cols].copy()
    elif filter_mode == "Unusually Low Only (Dips)":
        table_view = enriched_df[enriched_df["anomaly_status"] == "Unusually Low"][display_cols].copy()
    else:
        table_view = enriched_df[display_cols].copy()

    # Sort dataframe
    if sort_mode == "Most Extreme Z-Score (|Z| descending)":
        table_view["abs_z"] = table_view["z_score"].abs()
        table_view = table_view.sort_values(by="abs_z", ascending=False).drop(columns=["abs_z"])
    elif sort_mode == "Highest Measured Load First":
        table_view = table_view.sort_values(by=selected_load_col, ascending=False)
    elif sort_mode == "Lowest Measured Load First":
        table_view = table_view.sort_values(by=selected_load_col, ascending=True)
    else:
        table_view = table_view.sort_values(by="observation_index", ascending=True)

    if table_view.empty:
        st.info(f"✅ No observations matched the selected filter (configured threshold |Z| > {z_threshold:.1f}).")
    else:
        st.dataframe(table_view, hide_index=True, use_container_width=True)

    # Dual CSV Download buttons (Requirement 13)
    st.markdown("---")
    st.markdown("#### 📥 CSV Export Options")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        full_csv = enriched_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Analyzed Dataset (CSV)",
            data=full_csv,
            file_name="analyzed_network_load_results.csv",
            mime="text/csv",
            help="Download complete dataset including calculated Z-scores and classifications."
        )
    with col_dl2:
        if not anomalies_df.empty:
            anom_csv = anomalies_df[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Anomaly Table Only (CSV)",
                data=anom_csv,
                file_name="network_anomalies_report.csv",
                mime="text/csv",
                help="Download table containing only flagged operational anomalies."
            )
        else:
            st.button("📥 Download Anomaly Table Only (CSV)", disabled=True)


# =========================================================
# SECTION 3: DETAILED ANALYSIS
# =========================================================
with section_tabs[2]:
    st.markdown("### 3. Detailed Analysis & Diagnostics")
    st.markdown(
        "Examine temporal trends, test goodness-of-fit to the Normal distribution, "
        "and verify alignment with the 68–95–99.7% Empirical Rule."
    )

    # A. Network Load Over Time
    st.markdown("#### A. Network Load Trajectory Over Time")
    st.markdown(
        "Chronological sequence of network load. Upper and lower threshold lines mark statistical boundaries."
    )

    # Node comparison option if node column exists
    compare_nodes = False
    if node_column and df_raw[node_column].nunique() > 1:
        compare_nodes = st.checkbox("Compare all distributed server nodes on the same chart", value=False)

    ts_df = clean_df.copy()
    has_dates = False

    if val_res["timestamp_valid"] and "parsed_timestamp" in ts_df.columns:
        ts_df = ts_df.sort_values(by="parsed_timestamp")
        x_axis_series = ts_df["parsed_timestamp"]
        x_label_text = "Timestamp"
        has_dates = True
    elif timestamp_column and timestamp_column in ts_df.columns:
        x_axis_series = ts_df[timestamp_column].astype(str)
        x_label_text = f"Timestamp ({timestamp_column})"
    else:
        x_axis_series = np.arange(1, len(ts_df) + 1)
        x_label_text = "Observation Sequence Index (#)"

    y_values = ts_df[selected_load_col].to_numpy(dtype=float)

    fig2, ax2 = plt.subplots(figsize=(10.5, 4.8), dpi=125)

    if compare_nodes and node_column:
        # Plot multi-node breakdown
        distinct_nodes = df_raw[node_column].dropna().unique()
        palette = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4"]
        for idx, n_name in enumerate(distinct_nodes[:6]):
            node_sub = clean_df[clean_df[node_column] == n_name]
            if not node_sub.empty:
                x_sub = node_sub["parsed_timestamp"] if (val_res["timestamp_valid"] and "parsed_timestamp" in node_sub) else node_sub.index
                y_sub = node_sub[selected_load_col].to_numpy(dtype=float)
                ax2.plot(x_sub, y_sub, label=f"Node {n_name}", color=palette[idx % len(palette)], alpha=0.8, linewidth=1.3)
    else:
        ax2.plot(x_axis_series, y_values, color="#64748B", linewidth=1.2, alpha=0.85, label=f"Observed {selected_load_col}")

    # Reference lines
    upper_bound = mean_val + z_threshold * active_std_val
    lower_bound = mean_val - z_threshold * active_std_val

    ax2.axhline(mean_val, color="#0F172A", linestyle="-", linewidth=1.5, label=f"Mean Baseline ({mean_val:.1f} {load_unit})")
    ax2.axhline(upper_bound, color="#DC2626", linestyle="--", linewidth=1.3, label=f"Upper Threshold (+{z_threshold}σ: {upper_bound:.1f})")
    ax2.axhline(lower_bound, color="#0284C7", linestyle="--", linewidth=1.3, label=f"Lower Threshold (-{z_threshold}σ: {lower_bound:.1f})")

    # Highlight anomalies in time series
    z_for_ts = (y_values - mean_val) / active_std_val if active_std_val > 1e-9 else np.zeros_like(y_values)
    high_mask = z_for_ts > z_threshold
    low_mask = z_for_ts < -z_threshold

    if high_mask.any():
        ax2.scatter(np.array(x_axis_series)[high_mask], y_values[high_mask], color="#DC2626", s=55, edgecolors="#000", zorder=5, label="Unusually High")
    if low_mask.any():
        ax2.scatter(np.array(x_axis_series)[low_mask], y_values[low_mask], color="#0284C7", s=55, edgecolors="#000", zorder=5, label="Unusually Low")

    ax2.set_title(f"Time-Series Network Load Trajectory with Anomaly Boundaries (|Z| > {z_threshold})", fontsize=11, fontweight="bold", pad=12)
    ax2.set_xlabel(x_label_text, fontsize=10)
    ax2.set_ylabel(f"Load ({load_unit})", fontsize=10)
    ax2.grid(True, linestyle=":", alpha=0.55)
    if has_dates:
        fig2.autofmt_xdate()
    ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.markdown(
        "<small style='color:#64748B;'>Note: Measurements are plotted chronologically as recorded. "
        "No automated time-bin aggregation has been performed.</small>",
        unsafe_allow_html=True
    )

    # B. Goodness-of-Fit Diagnostics (Expandable)
    with st.expander("🔬 B. Normal Distribution Goodness-of-Fit Diagnostics", expanded=False):
        col_qq, col_hyp = st.columns([3, 2])
        
        with col_qq:
            fig_qq, ax_qq = plt.subplots(figsize=(6.5, 4.6), dpi=120)
            stats.probplot(load_values, dist="norm", plot=ax_qq)
            ax_qq.get_lines()[0].set_color("#2563EB")
            ax_qq.get_lines()[0].set_markersize(4.0)
            ax_qq.get_lines()[1].set_color("#DC2626")
            ax_qq.get_lines()[1].set_linewidth(1.8)
            ax_qq.set_title("Quantile-Quantile (Q-Q) Plot vs Theoretical Normal", fontsize=10, fontweight="bold")
            ax_qq.grid(True, linestyle=":", alpha=0.6)
            fig_qq.tight_layout()
            st.pyplot(fig_qq)
            plt.close(fig_qq)

        with col_hyp:
            fit_results = assess_goodness_of_fit(load_values, mean_val, active_std_val)
            st.markdown("##### Hypothesis Testing Results")
            st.markdown("""
            - **Null Hypothesis ($H_0$):** Network load data follows a Normal distribution.
            - **Alternative Hypothesis ($H_1$):** Network load data departs significantly from a Normal distribution.
            """)
            if fit_results.get("applicable", False):
                ks_p = fit_results["ks_pvalue"]
                st.markdown(f"""
                - **Kolmogorov-Smirnov (KS) Test:**
                  * Statistic $D$: `{fit_results['ks_stat']:.4f}`
                  * $p$-value: `{ks_p:.4e}`
                  * Result ($\\alpha=0.05$): **{'✅ Fail to reject H₀ (Data consistent with Normal)' if fit_results['ks_is_normal'] else '⚠️ Reject H₀ (Significant departure from Normal)'}**
                """)
                if fit_results.get("shapiro_applicable", False) and fit_results["shapiro_pvalue"] is not None:
                    shap_p = fit_results["shapiro_pvalue"]
                    st.markdown(f"""
                    - **Shapiro-Wilk Test:**
                      * Statistic $W$: `{fit_results['shapiro_stat']:.4f}`
                      * $p$-value: `{shap_p:.4e}`
                    """)
                st.markdown(f"""
                - **Shape Metrics:**
                  * Skewness: `{skewness_val:.3f}` *(Normal = 0)*
                  * Excess Kurtosis: `{kurtosis_val:.3f}` *(Normal = 0)*
                """)
            st.markdown("""
            <div class="note-box" style="font-size:0.82rem;">
                <b>Limitations:</b> Failing to reject H₀ does NOT mathematically prove the data is purely Gaussian.
                Real networks have non-zero lower bounds (load ≥ 0) and bursty packet tails.
            </div>
            """, unsafe_allow_html=True)

    # C. Empirical Rule Verification (Expandable)
    with st.expander("📏 C. Empirical Rule (68–95–99.7%) Coverage Benchmark", expanded=False):
        rule_bands = calculate_empirical_rule_coverage(load_values, mean_val, active_std_val)
        if rule_bands:
            table_rows = []
            for b_name, b_info in rule_bands.items():
                table_rows.append({
                    "Interval Band": b_info["label"],
                    "Range Limits": f"[{b_info['lower']:.2f}, {b_info['upper']:.2f}] {load_unit}",
                    "Theoretical Expected": f"{b_info['theoretical_pct']:.2f}%",
                    "Observed Actual": f"{b_info['observed_pct']:.2f}% ({b_info['observed_count']}/{valid_n})",
                    "Discrepancy": f"{b_info['discrepancy_pct']:+.2f}%"
                })
            st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)
            st.markdown(
                "<small style='color:#64748B;'>Theoretical coverage percentages are expectations for a purely Normal distribution. "
                "Discrepancies highlight natural operational variance and diurnal fluctuations.</small>",
                unsafe_allow_html=True
            )




# ---------------------------------------------------------
# Report-Ready Results Summary (Requirement 13)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 📑 Report-Ready Results Summary")
st.markdown(f"""
| Parameter | Analyzed Value | Technical Description |
| :--- | :--- | :--- |
| **Active Dataset** | `{active_dataset_name}` | Source telemetry dataset |
| **Analyzed Metric** | `{selected_load_col}` ({load_unit}) | Target traffic variable |
| **Valid Observations (N)** | `{valid_n:,}` | Cleaned numerical measurements analyzed |
| **Missing Values Cleaned** | `{missing_n}` | Rows excluded to preserve statistical integrity |
| **Sample Mean (x̄)** | `{mean_val:.2f} {load_unit}` | Central baseline throughput |
| **Sample Std Dev (s)** | `{sample_std_val:.2f} {load_unit}` | Bessel-corrected dispersion ($N-1$) |
| **Population Std Dev (σ)** | `{pop_std_val:.2f} {load_unit}` | Unadjusted lifetime dispersion ($N$) |
| **Z-Score Threshold** | `|Z| > {z_threshold:.1f}` | Statistical outlier boundary |
| **Flagged Anomalies** | `{total_anomalies}` ({anomaly_rate:.1f}%) | `{high_anomalies}` High surges, `{low_anomalies}` Low dips |
| **Three-Sigma Headroom** | `{headroom_3s:.2f} {load_unit}` | Upper 99.73% capacity planning ceiling ($\bar{x} + 3s$) |
""")

st.markdown(
    "<div style='text-align: center; color: #94A3B8; font-size: 0.85rem; margin-top: 24px;'>"
    "Network Load Statistical Analyzer &bull; Statistical Modeling of Network Load Using Normal Distribution &bull; Free & Locally Executable"
    "</div>",
    unsafe_allow_html=True
)
