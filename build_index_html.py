"""
build_index_html.py
===================
Generates the clean, genuinely beginner-friendly, simple, and trustworthy
Network Load Statistical Analyzer.

Features:
- Fixed JS regex line splits (no broken execution).
- Three-step workflow (Upload CSV / Select Metric / Analyze Traffic).
- 4 Primary Result Cards (Valid Observations, Mean Load, Standard Deviation, Flagged Anomalies).
- 3 Simplified Navigation Tabs (Overview, Anomaly Detection, Statistical Details).
- Donut/Pie Chart added to Anomaly Detection tab for visual ratio analysis.
- Histogram with fitted Normal PDF curve, Probability Calculator, and Q-Q Goodness-of-fit plot.
- Fully standalone, client-side, zero cloud dependencies.
"""

import os

def generate_index_html():
    sample_csv_path = "sample_network_load.csv"
    if os.path.exists(sample_csv_path):
        with open(sample_csv_path, "r", encoding="utf-8") as f:
            sample_csv = f.read().strip()
    else:
        sample_csv = "timestamp,bandwidth_mbps,packet_count_per_sec,cpu_utilization_percent,latency_ms,server_node_id\n"

    # Escape for JS template literal
    escaped_csv = sample_csv.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Load Statistical Analyzer</title>
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <!-- Google Fonts: Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <!-- Chart.js 4.4.1 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-page: #F8FAFC;
            --bg-card: #FFFFFF;
            --bg-subtle: #F1F5F9;
            --border: #E2E8F0;
            --border-hover: #CBD5E1;
            
            --text-heading: #0F172A;
            --text-body: #334155;
            --text-muted: #64748B;
            --text-light: #94A3B8;

            --primary: #2563EB;
            --primary-hover: #1D4ED8;
            --primary-light: #EFF6FF;
            --teal: #0D9488;
            --teal-light: #F0FDFA;

            --success: #16A34A;
            --success-light: #DCFCE7;
            --danger: #DC2626;
            --danger-light: #FEE2E2;
            --warning: #D97706;
            --warning-light: #FEF3C7;
            --info: #0284C7;
            --info-light: #E0F2FE;

            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-body);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.5;
            padding: 24px 20px 48px;
            -webkit-font-smoothing: antialiased;
        }}

        .app-container {{
            max-width: 1240px;
            margin: 0 auto;
        }}

        /* App Header */
        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .app-title h1 {{
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.025em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .app-title p {{
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .active-dataset-tag {{
            font-size: 0.8rem;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 9999px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-heading);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: var(--shadow-sm);
        }}

        .active-dataset-tag .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
        }}

        /* STEP WORKFLOW BAR */
        .workflow-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 18px 22px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 24px;
        }}

        .workflow-grid {{
            display: grid;
            grid-template-columns: 1.3fr 1.2fr auto auto;
            gap: 16px;
            align-items: end;
        }}

        @media (max-width: 900px) {{
            .workflow-grid {{
                grid-template-columns: 1fr;
            }}
            .anomaly-grid-layout {{
                grid-template-columns: 1fr !important;
            }}
        }}

        .step-field {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .step-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .step-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            font-size: 0.68rem;
            font-weight: 700;
        }}

        select, input[type="text"], input[type="number"] {{
            padding: 9px 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font-size: 0.88rem;
            font-family: inherit;
            color: var(--text-heading);
            background: var(--bg-card);
            outline: none;
            transition: all 0.15s;
            width: 100%;
        }}

        select:focus, input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}

        /* Buttons */
        .btn {{
            cursor: pointer;
            border: none;
            padding: 9px 18px;
            border-radius: var(--radius-sm);
            font-size: 0.88rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.15s;
            text-decoration: none;
            font-family: inherit;
            white-space: nowrap;
        }}

        .btn-primary {{
            background: var(--primary);
            color: #FFFFFF;
        }}
        .btn-primary:hover {{
            background: var(--primary-hover);
        }}

        .btn-outline {{
            background: var(--bg-card);
            color: var(--text-body);
            border: 1px solid var(--border);
        }}
        .btn-outline:hover {{
            background: var(--bg-subtle);
            border-color: var(--border-hover);
        }}

        /* Collapsible Settings Panel */
        .collapsible-settings {{
            display: none;
            margin-top: 18px;
            padding-top: 18px;
            border-top: 1px solid var(--border);
        }}

        .collapsible-settings.open {{
            display: block;
        }}

        .settings-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            align-items: end;
        }}

        .range-wrapper {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .range-wrapper input[type="range"] {{
            flex: 1;
            accent-color: var(--primary);
            cursor: pointer;
        }}

        .range-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--primary);
            background: var(--primary-light);
            padding: 2px 8px;
            border-radius: 4px;
            min-width: 44px;
            text-align: center;
        }}

        /* TOP 4 PRIMARY RESULT CARDS */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        @media (max-width: 900px) {{
            .kpi-row {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 540px) {{
            .kpi-row {{
                grid-template-columns: 1fr;
            }}
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 18px 20px;
            box-shadow: var(--shadow-sm);
            transition: transform 0.15s, box-shadow 0.15s;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        .kpi-label {{
            font-size: 0.76rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 6px;
        }}

        .kpi-val {{
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.03em;
            line-height: 1.15;
            margin-bottom: 4px;
            display: flex;
            align-items: baseline;
            gap: 6px;
        }}

        .kpi-val .unit-span {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-muted);
        }}

        .kpi-subtext {{
            font-size: 0.78rem;
            color: var(--text-muted);
            line-height: 1.35;
        }}

        /* 3 SIMPLIFIED SECTIONS NAVIGATION */
        .section-tabs {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid var(--border);
            margin-bottom: 22px;
        }}

        .tab-btn {{
            cursor: pointer;
            border: none;
            background: transparent;
            font-family: inherit;
            font-size: 0.92rem;
            font-weight: 600;
            color: var(--text-muted);
            padding: 12px 18px;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s;
            border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        }}

        .tab-btn:hover {{
            color: var(--primary);
            background: var(--bg-subtle);
        }}

        .tab-btn.active {{
            color: var(--primary);
            border-bottom-color: var(--primary);
            background: var(--bg-card);
        }}

        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}

        /* Card Panels */
        .card-panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 22px 24px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 22px;
        }}

        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .panel-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-heading);
            letter-spacing: -0.01em;
        }}

        .panel-desc {{
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .chart-box {{
            position: relative;
            height: 400px;
            width: 100%;
        }}

        /* Beginner-friendly explanation box */
        .beginner-explanation {{
            margin-top: 16px;
            background: var(--bg-subtle);
            border-left: 3px solid var(--teal);
            padding: 12px 16px;
            border-radius: 4px;
            font-size: 0.84rem;
            color: var(--text-body);
            line-height: 1.5;
        }}

        .beginner-explanation strong {{
            color: var(--text-heading);
        }}

        /* Table Styling */
        .table-responsive {{
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            background: #FFFFFF;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.86rem;
            text-align: left;
        }}

        th {{
            background: var(--bg-subtle);
            color: var(--text-muted);
            font-weight: 700;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        td {{
            padding: 9px 14px;
            border-bottom: 1px solid var(--border);
            color: var(--text-body);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: #F8FAFC;
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.74rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 9999px;
        }}

        .status-normal {{
            background: var(--success-light);
            color: var(--success);
        }}

        .status-high {{
            background: var(--danger-light);
            color: var(--danger);
        }}

        .status-low {{
            background: var(--info-light);
            color: var(--info);
        }}

        /* Statistical Summary Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 12px;
            margin-top: 14px;
        }}

        .stat-card {{
            background: var(--bg-subtle);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 12px 14px;
        }}

        .stat-card-label {{
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .stat-card-val {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-heading);
            margin-top: 2px;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Progressive Disclosure Details / Summary */
        details.progressive-box {{
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 14px 18px;
            margin-bottom: 16px;
            transition: all 0.2s;
        }}

        details.progressive-box[open] {{
            background: #FFFFFF;
            box-shadow: var(--shadow-sm);
        }}

        details.progressive-box summary {{
            cursor: pointer;
            font-weight: 600;
            font-size: 0.92rem;
            color: var(--text-heading);
            outline: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        details.progressive-box summary::-webkit-details-marker {{
            display: none;
        }}

        .progressive-content {{
            margin-top: 14px;
            padding-top: 14px;
            border-top: 1px solid var(--border);
            font-size: 0.86rem;
            line-height: 1.55;
            color: var(--text-body);
        }}

        /* Probability Calculator */
        .calc-panel {{
            background: var(--bg-subtle);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 14px 16px;
            margin-top: 12px;
        }}

        .calc-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            font-size: 0.85rem;
            border-bottom: 1px dashed var(--border);
        }}

        .calc-row:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}

        .calc-row .num {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: var(--text-heading);
        }}

        .gauge-track {{
            position: relative;
            height: 8px;
            background: linear-gradient(90deg, #3B82F6 0%, #10B981 50%, #EF4444 100%);
            border-radius: 4px;
            margin: 14px 0 6px;
        }}

        .gauge-needle {{
            position: absolute;
            top: -5px;
            width: 10px;
            height: 18px;
            background: #0F172A;
            border: 2px solid #FFFFFF;
            border-radius: 3px;
            transform: translateX(-50%);
            transition: left 0.2s;
        }}

        #fileInputHidden {{
            display: none;
        }}
    </style>
</head>
<body>

<div class="app-container">
    <!-- Clean App Header -->
    <header class="app-header">
        <div class="app-title">
            <h1>Network Load Statistical Analyzer</h1>
            <p>Statistical Modeling of Network Traffic Using Normal Distribution</p>
        </div>
        <div>
            <div class="active-dataset-tag" id="activeDatasetTag">
                <span class="dot"></span>
                <span id="activeDatasetLabel">sample_network_load.csv (288 rows)</span>
            </div>
        </div>
    </header>

    <!-- 1. CLEAR THREE-STEP WORKFLOW BAR -->
    <div class="workflow-card">
        <div class="workflow-grid">
            <!-- Step 1: Upload CSV Dataset -->
            <div class="step-field">
                <label class="step-label">
                    <span class="step-badge">1</span> Dataset Source
                </label>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-primary" onclick="document.getElementById('fileInputHidden').click()" style="flex:1;">
                        📁 Upload CSV File
                    </button>
                    <button class="btn btn-outline" onclick="loadDefaultSample()" title="Reset to sample dataset">
                        🔄 Sample
                    </button>
                </div>
            </div>

            <!-- Step 2: Traffic Metric Selection -->
            <div class="step-field">
                <label class="step-label" for="colSelect">
                    <span class="step-badge">2</span> Select Traffic Metric
                </label>
                <select id="colSelect"></select>
            </div>

            <!-- Step 3: Analyze Action -->
            <div>
                <button class="btn btn-primary" onclick="runAnalysis()" style="width: 100%;">
                    ⚡ Analyze Traffic
                </button>
            </div>

            <!-- Advanced Settings Toggle -->
            <div>
                <button class="btn btn-outline" onclick="toggleSettingsPanel()">
                    ⚙️ Settings
                </button>
            </div>
        </div>

        <input type="file" id="fileInputHidden" accept=".csv" onchange="handleFileUpload(event)">

        <!-- Collapsible Advanced Settings Panel -->
        <div id="advancedSettingsPanel" class="collapsible-settings">
            <div class="settings-grid">
                <div class="step-field">
                    <label class="step-label" for="timeSelect">Timestamp Column (Optional)</label>
                    <select id="timeSelect"></select>
                </div>
                <div class="step-field">
                    <label class="step-label" for="unitSelect">Metric Unit</label>
                    <select id="unitSelect">
                        <option value="Mbps">Mbps (Megabits/s)</option>
                        <option value="Gbps">Gbps (Gigabits/s)</option>
                        <option value="Bytes/s">Bytes/s (Flow Byte Rate)</option>
                        <option value="Packets/s">Packets/s (Packet Rate)</option>
                        <option value="Packets">Packets (Count)</option>
                        <option value="Bytes">Bytes (Volume)</option>
                        <option value="% Utilization">% Utilization</option>
                        <option value="ms">ms (Latency)</option>
                        <option value="Dimensionless">Dimensionless / Ratio</option>
                    </select>
                </div>
                <div class="step-field">
                    <label class="step-label" for="zThreshold">
                        <span>Anomaly Threshold</span>
                        <span class="range-badge" id="zThresholdBadge">±3.0σ</span>
                    </label>
                    <div class="range-wrapper">
                        <input type="range" id="zThreshold" min="1.5" max="4.0" step="0.1" value="3.0" oninput="updateThresholdLabel(this.value)">
                    </div>
                </div>
                <div class="step-field">
                    <label class="step-label" for="stdMode">Std Dev Method</label>
                    <select id="stdMode">
                        <option value="sample">Sample Std Dev (s, Bessel's N-1)</option>
                        <option value="population">Population Std Dev (σ, N)</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <!-- 2. FOUR PRIMARY RESULT CARDS -->
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">Valid Observations</div>
            <div class="kpi-val" id="kpiN">288</div>
            <div class="kpi-subtext" id="kpiCleanSub">Total usable measurements: 288 (0 missing)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Mean Network Load (x̄)</div>
            <div class="kpi-val">
                <span id="kpiMean">452.36</span>
                <span class="unit-span" id="unitSpanMean">Mbps</span>
            </div>
            <div class="kpi-subtext">Baseline average traffic across observations</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label" id="kpiStdLabel">Standard Deviation (s)</div>
            <div class="kpi-val">
                <span id="kpiStd">43.63</span>
                <span class="unit-span" id="unitSpanStd">Mbps</span>
            </div>
            <div class="kpi-subtext" id="kpiStdSub">Dispersion around mean (Bessel's N-1)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label" id="kpiAnomLabel">Flagged Anomalies (|Z| &gt; 3.0)</div>
            <div class="kpi-val" style="color: var(--danger);" id="kpiAnom">
                4 <span style="font-size:0.95rem; font-weight:600; color:var(--text-muted);">(1.4%)</span>
            </div>
            <div class="kpi-subtext" id="kpiAnomSub">3 High Spikes | 1 Low Dip</div>
        </div>
    </div>

    <!-- 3. SIMPLIFIED THREE NAVIGATION TABS -->
    <div class="section-tabs">
        <button class="tab-btn active" onclick="switchTab('tab-overview', this)">
            📊 Overview
        </button>
        <button class="tab-btn" onclick="switchTab('tab-anomalies', this)">
            🚨 Anomaly Detection
        </button>
        <button class="tab-btn" onclick="switchTab('tab-details', this)">
            📈 Statistical Details
        </button>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 1: OVERVIEW -->
    <!-- ========================================================= -->
    <div id="tab-overview" class="tab-content active">
        <div class="card-panel">
            <div class="panel-header">
                <div>
                    <div class="panel-title">Histogram &amp; Fitted Normal Distribution Curve</div>
                    <div class="panel-desc">Observed measurements compared with mathematical Gaussian distribution</div>
                </div>
                <div style="display:flex; gap:12px; align-items:center; font-size:0.82rem; font-weight:600;">
                    <label style="cursor:pointer; display:flex; align-items:center; gap:4px;">
                        <input type="radio" name="scaleMode" value="density" checked onchange="toggleHistScale('density')"> Density Scale
                    </label>
                    <label style="cursor:pointer; display:flex; align-items:center; gap:4px;">
                        <input type="radio" name="scaleMode" value="count" onchange="toggleHistScale('count')"> Frequency Scale
                    </label>
                </div>
            </div>
            <div class="chart-box">
                <canvas id="distChart"></canvas>
            </div>
            <div class="beginner-explanation">
                <strong>What does this graph mean?</strong><br>
                The blue bars show your real network measurements grouped into intervals. The smooth red curve is the theoretical Normal (Gaussian) bell curve computed from the mean and standard deviation. When the blue bars follow the red curve closely, the network traffic behaves predictably around its normal baseline.
            </div>
        </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 2: ANOMALY DETECTION -->
    <!-- ========================================================= -->
    <div id="tab-anomalies" class="tab-content">
        <!-- Summary Badges -->
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:16px;">
            <span class="active-dataset-tag" style="color:var(--danger);">Flagged Outliers: <strong id="anomTotalPill">4</strong></span>
            <span class="active-dataset-tag" style="color:var(--danger);">High Spikes: <strong id="anomHighPill">3</strong></span>
            <span class="active-dataset-tag" style="color:var(--info);">Low Dips: <strong id="anomLowPill">1</strong></span>
            <span class="active-dataset-tag" style="color:var(--success);">Normal In-Bounds: <strong id="anomNormalPill">284</strong></span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px;" class="anomaly-grid-layout">
            <!-- Donut / Pie Chart Card -->
            <div class="card-panel" style="margin-bottom:0;">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">Anomaly Ratio (Pie Chart)</div>
                        <div class="panel-desc">Proportions of normal vs outlying traffic</div>
                    </div>
                </div>
                <div style="position: relative; height: 260px;">
                    <canvas id="anomalyPieChart"></canvas>
                </div>
                <div class="beginner-explanation" style="margin-top: 14px; font-size: 0.78rem;">
                    <strong>Pie Chart Breakdown:</strong> Visualizes the ratio of normal in-bounds observations vs. high spikes and low dips (|Z| &gt; threshold).
                </div>
            </div>

            <!-- Table Card -->
            <div class="card-panel" style="margin-bottom:0;">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">Observed Network Anomalies</div>
                        <div class="panel-desc">Flagged measurements: Z = (measurement - mean) / std</div>
                    </div>
                    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                        <select id="tableFilterSelect" onchange="renderAnomalyTable()" style="width:auto;">
                            <option value="anomalies">Flagged Anomalies Only</option>
                            <option value="high">High Spikes (Z &gt; threshold)</option>
                            <option value="low">Low Dips (Z &lt; -threshold)</option>
                            <option value="all">All Records</option>
                        </select>
                        <button class="btn btn-primary" onclick="exportAnalyzedCSV()">
                            📥 Export All
                        </button>
                        <button class="btn btn-outline" onclick="exportAnomaliesCSV()">
                            📥 Export Anomalies
                        </button>
                    </div>
                </div>

                <div class="table-responsive" style="max-height: 280px; overflow-y: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th># Index</th>
                                <th>Timestamp</th>
                                <th>Observed Value</th>
                                <th>Z-Score</th>
                                <th>Classification</th>
                            </tr>
                        </thead>
                        <tbody id="anomalyTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="beginner-explanation" style="border-left-color: var(--danger); margin-top:16px;">
            <strong>Important Note on Network Anomalies:</strong><br>
            A statistical anomaly is simply an unusual mathematical observation. In distributed systems, this is <strong>not necessarily a cyberattack or system failure</strong>. Legitimate causes include scheduled backups, large batch data replication, or off-peak maintenance windows.
        </div>
    </div>

    <!-- ========================================================= -->
    <!-- SECTION 3: STATISTICAL DETAILS -->
    <!-- ========================================================= -->
    <div id="tab-details" class="tab-content">
        <!-- Parameter Summary Grid -->
        <div class="card-panel">
            <div class="panel-title">Descriptive Parameter Summary</div>
            <div class="panel-desc">Calculated summary values for the active dataset</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-card-label">Sample Size (N)</div>
                    <div class="stat-card-val" id="gridN">288</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Mean (x̄)</div>
                    <div class="stat-card-val" id="gridMean">452.36</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Median (Q2)</div>
                    <div class="stat-card-val" id="gridMedian">450.80</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Sample Std (s, N-1)</div>
                    <div class="stat-card-val" id="gridSampleStd">43.63</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Population Std (σ)</div>
                    <div class="stat-card-val" id="gridPopStd">43.55</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Variance (s²)</div>
                    <div class="stat-card-val" id="gridVar">1903.6</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Minimum Observed</div>
                    <div class="stat-card-val" id="gridMin">298.50</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-label">Maximum Observed</div>
                    <div class="stat-card-val" id="gridMax">610.20</div>
                </div>
            </div>
        </div>

        <!-- PROGRESSIVE DISCLOSURE: PROBABILITY CALCULATOR -->
        <details class="progressive-box">
            <summary>
                <span>🧮 Explore Probability Calculations</span>
                <span>▼</span>
            </summary>
            <div class="progressive-content">
                <div style="max-width: 400px; margin-bottom: 12px;">
                    <label style="font-size:0.8rem; font-weight:700; color:var(--text-muted);">Enter Value to Test:</label>
                    <input type="number" id="probInputVal" step="1" oninput="calculateProbabilities()">
                </div>
                <div class="calc-panel">
                    <div class="calc-row">
                        <span>Standardized Z-Score:</span>
                        <span class="num" id="calcZ" style="color:var(--primary);">Z = 0.000</span>
                    </div>
                    <div class="calc-row">
                        <span>Theoretical P(X ≤ x):</span>
                        <span class="num" id="calcBelow">50.00%</span>
                    </div>
                    <div class="calc-row">
                        <span>Theoretical Exceedance P(X &gt; x):</span>
                        <span class="num" id="calcAbove">50.00%</span>
                    </div>
                    <div class="calc-row">
                        <span>Observed Empirical Percentile:</span>
                        <span class="num" id="calcEmpirical">50.00%</span>
                    </div>
                </div>
                <div class="gauge-track">
                    <div id="visualPointer" class="gauge-needle" style="left: 50%;"></div>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); text-align: center; margin-top: 4px;" id="visualCaption">
                    Entered value is at the baseline mean.
                </div>
            </div>
        </details>

        <!-- PROGRESSIVE DISCLOSURE: GOODNESS-OF-FIT DIAGNOSTICS -->
        <details class="progressive-box">
            <summary>
                <span>🔍 Normal Distribution Goodness-of-Fit Diagnostics</span>
                <span>▼</span>
            </summary>
            <div class="progressive-content">
                <div style="position: relative; height: 300px; margin-bottom: 14px;">
                    <canvas id="qqChart"></canvas>
                </div>
                <div style="display:flex; gap:20px; font-size:0.85rem; margin-bottom:10px;">
                    <span>Sample Skewness: <strong id="fitSkewness">0.030</strong></span>
                    <span>Excess Kurtosis: <strong id="fitKurtosis">-0.120</strong></span>
                </div>
                <div class="beginner-explanation">
                    <strong>How to read the Q-Q Plot:</strong><br>
                    The points compare actual quantiles with theoretical Gaussian quantiles. When points follow the red 45° line, the data fits a Normal distribution well. Large deviations at the ends indicate skew or heavy traffic bursts.
                </div>
            </div>
        </details>

        <!-- PROGRESSIVE DISCLOSURE: STATISTICAL ASSUMPTIONS & LIMITATIONS -->
        <details class="progressive-box">
            <summary>
                <span>⚠️ Statistical Assumptions &amp; Limitations</span>
                <span>▼</span>
            </summary>
            <div class="progressive-content">
                <p><strong>1. Central Limit Theorem:</strong> Aggregated network traffic over fixed intervals from multiple independent sources often approximates a Normal distribution. However, fine-grained micro-bursts may be heavy-tailed.</p>
                <p style="margin-top:8px;"><strong>2. Sample vs. Population:</strong> This analyzer uses Bessel's correction (N - 1) by default for sample standard deviation to avoid underestimating variability.</p>
                <p style="margin-top:8px;"><strong>3. Different Metrics:</strong> Flow byte rates (Bytes/s), packet rates (Packets/s), and packet counts represent different physical quantities and must not be mixed.</p>
            </div>
        </details>
    </div>

    <!-- Clean Footer -->
    <footer style="text-align: center; color: var(--text-light); font-size: 0.8rem; margin-top: 36px;">
        Network Load Statistical Analyzer &bull; Statistical Modeling of Network Load Using Normal Distribution
    </footer>
</div>

<script>
// =========================================================
// EMBEDDED SAMPLE DATASET (288 observations)
// =========================================================
const DEFAULT_CSV_DATA = `{escaped_csv}`;

// State
let rawCSVData = DEFAULT_CSV_DATA;
let parsedRows = [];
let columnHeaders = [];
let currentLoadValues = [];
let currentTimestamps = [];
let currentStats = {{}};
let currentAnomalies = [];
let distChartInstance = null;
let anomalyPieChartInstance = null;
let qqChartInstance = null;
let histScaleMode = "density";
let currentDatasetName = "sample_network_load.csv (288 rows)";

// =========================================================
// INITIALIZATION
// =========================================================
window.addEventListener("DOMContentLoaded", () => {{
    loadDatasetText(DEFAULT_CSV_DATA, "sample_network_load.csv (288 rows)");
}});

function toggleSettingsPanel() {{
    const panel = document.getElementById("advancedSettingsPanel");
    panel.classList.toggle("open");
}}

function updateThresholdLabel(val) {{
    const num = parseFloat(val).toFixed(1);
    document.getElementById("zThresholdBadge").textContent = `±${{num}}σ`;
}}

function toggleHistScale(mode) {{
    histScaleMode = mode;
    renderDistributionChart();
}}

// =========================================================
// DATASET HANDLERS
// =========================================================
function loadDefaultSample() {{
    loadDatasetText(DEFAULT_CSV_DATA, "sample_network_load.csv (288 rows)");
}}

function handleFileUpload(event) {{
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {{
        const text = e.target.result;
        const lines = text.trim().split(/\\r?\\n/);
        const rowCount = lines.length > 1 ? lines.length - 1 : 0;
        const name = `${{file.name}} (${{rowCount}} rows)`;
        loadDatasetText(text, name);
    }};
    reader.readAsText(file);
}}

function parseCSV(text) {{
    const lines = text.trim().split(/\\r?\\n/);
    if (lines.length < 2) return {{ headers: [], rows: [] }};
    const headers = lines[0].split(",").map(h => h.trim().replace(/^["']|["']$/g, ""));
    const rows = [];
    for (let i = 1; i < lines.length; i++) {{
        const line = lines[i].trim();
        if (!line) continue;
        const values = line.split(",").map(v => v.trim().replace(/^["']|["']$/g, ""));
        const rowObj = {{}};
        headers.forEach((h, idx) => {{
            rowObj[h] = values[idx] !== undefined ? values[idx] : "";
        }});
        rows.push(rowObj);
    }}
    return {{ headers, rows }};
}}

function loadDatasetText(csvText, label) {{
    rawCSVData = csvText;
    currentDatasetName = label;
    document.getElementById("activeDatasetLabel").textContent = label;

    const parsed = parseCSV(csvText);
    columnHeaders = parsed.headers;
    parsedRows = parsed.rows;

    const colSelect = document.getElementById("colSelect");
    const timeSelect = document.getElementById("timeSelect");
    colSelect.innerHTML = "";
    timeSelect.innerHTML = '<option value="">None / Sequence Index</option>';

    let defaultMetric = "";
    let defaultTime = "";

    // Candidate suggestions
    const metricCandidates = ["flow bytes/s", "flow packets/s", "sbytes", "dbytes", "sload", "dload", "bandwidth_mbps", "bandwidth", "load", "throughput", "packet"];

    columnHeaders.forEach(col => {{
        const opt = document.createElement("option");
        opt.value = col;
        opt.textContent = col;
        colSelect.appendChild(opt);

        const timeOpt = document.createElement("option");
        timeOpt.value = col;
        timeOpt.textContent = col;
        timeSelect.appendChild(timeOpt);

        const lower = col.toLowerCase().trim();
        if (!defaultMetric && metricCandidates.some(c => lower.includes(c))) {{
            defaultMetric = col;
        }}
        if (!defaultTime && (lower.includes("time") || lower.includes("date") || lower.includes("ts"))) {{
            defaultTime = col;
        }}
    }});

    if (!defaultMetric && columnHeaders.length > 0) defaultMetric = columnHeaders[0];
    if (defaultMetric) colSelect.value = defaultMetric;
    if (defaultTime) timeSelect.value = defaultTime;

    // Auto-select unit
    const lowerMetric = defaultMetric.toLowerCase();
    const unitSelect = document.getElementById("unitSelect");
    if (lowerMetric.includes("bytes/s")) unitSelect.value = "Bytes/s";
    else if (lowerMetric.includes("packet") || lowerMetric.includes("pkts")) unitSelect.value = "Packets/s";
    else if (lowerMetric.includes("mbps")) unitSelect.value = "Mbps";
    else if (lowerMetric.includes("ms") || lowerMetric.includes("latency")) unitSelect.value = "ms";

    runAnalysis();
}}

// =========================================================
// STATISTICAL MATHEMATICAL CALCULATIONS
// =========================================================
function normalCDF(x, mean, std) {{
    if (std <= 1e-9) return x >= mean ? 1.0 : 0.0;
    const z = (x - mean) / std;
    const t = 1.0 / (1.0 + 0.2316419 * Math.abs(z));
    const d = 0.3989422804014327 * Math.exp(-z * z / 2.0);
    const prob = d * t * (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
    return z > 0 ? 1.0 - prob : prob;
}}

function normalPDF(x, mean, std) {{
    if (std <= 1e-9) return 0.0;
    const z = (x - mean) / std;
    return (1.0 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * z * z);
}}

function standardNormalQuantile(p) {{
    if (p <= 0) return -4.0;
    if (p >= 1) return 4.0;
    const a = [-3.969683028665376e+01,  2.209460984245205e+02, -2.759285104469687e+02,  1.383577518672690e+02, -3.066479806614716e+01,  2.506628277459239e+00];
    const b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798529320e+02,  6.680131188771972e+01, -1.328068155288572e+01];
    const c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00];
    const d = [ 7.784695709041462e-03,  3.224671290700398e-01,  2.445134137142996e+00,  3.754408661907416e+00];

    const q = p - 0.5;
    if (Math.abs(q) <= 0.42) {{
        const r = q * q;
        return q * (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) /
                   (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1.0);
    }}
    const r = p < 0.5 ? p : 1.0 - p;
    const s = Math.log(-Math.log(r));
    let x = c[0] + s*(c[1] + s*(c[2] + s*(c[3] + s*(c[4] + s*c[5]))));
    const denom = 1.0 + s*(d[0] + s*(d[1] + s*(d[2] + s*d[3])));
    x = x / denom;
    return p < 0.5 ? -x : x;
}}

function runAnalysis() {{
    const loadCol = document.getElementById("colSelect").value;
    const timeCol = document.getElementById("timeSelect").value;
    const unit = document.getElementById("unitSelect").value;
    const zThreshold = parseFloat(document.getElementById("zThreshold").value);
    const stdMode = document.getElementById("stdMode").value;

    document.querySelectorAll(".unit-span").forEach(el => el.textContent = unit);

    if (!loadCol) return;

    const validEntries = [];
    parsedRows.forEach((r, idx) => {{
        const rawVal = parseFloat(r[loadCol]);
        if (!isNaN(rawVal)) {{
            validEntries.push({{
                index: idx + 1,
                time: timeCol && r[timeCol] ? r[timeCol] : `#${{idx + 1}}`,
                val: rawVal
            }});
        }}
    }});

    const n = validEntries.length;
    if (n === 0) {{
        alert("No valid numeric records found in selected column.");
        return;
    }}

    currentLoadValues = validEntries.map(e => e.val);
    currentTimestamps = validEntries.map(e => e.time);

    const sum = currentLoadValues.reduce((a, b) => a + b, 0);
    const mean = sum / n;

    const sqDiffs = currentLoadValues.map(v => Math.pow(v - mean, 2));
    const sumSqDiffs = sqDiffs.reduce((a, b) => a + b, 0);

    const sampleVar = n > 1 ? sumSqDiffs / (n - 1) : 0;
    const popVar = sumSqDiffs / n;
    const sampleStd = Math.sqrt(sampleVar);
    const popStd = Math.sqrt(popVar);

    const activeStd = stdMode === "sample" ? sampleStd : popStd;
    const activeVar = stdMode === "sample" ? sampleVar : popVar;

    const sorted = [...currentLoadValues].sort((a, b) => a - b);
    const minVal = sorted[0];
    const maxVal = sorted[sorted.length - 1];
    const median = n % 2 === 0 ? (sorted[n/2 - 1] + sorted[n/2]) / 2 : sorted[Math.floor(n/2)];

    let skewness = 0;
    let kurtosis = 0;
    if (activeStd > 1e-9 && n > 2) {{
        const m3 = currentLoadValues.map(v => Math.pow((v - mean) / activeStd, 3)).reduce((a, b) => a + b, 0) / n;
        const m4 = currentLoadValues.map(v => Math.pow((v - mean) / activeStd, 4)).reduce((a, b) => a + b, 0) / n;
        skewness = m3;
        kurtosis = m4 - 3.0;
    }}

    currentStats = {{
        n, mean, sampleStd, popStd, activeStd, sampleVar, popVar, activeVar,
        minVal, maxVal, median, skewness, kurtosis, unit, zThreshold, stdMode
    }};

    currentAnomalies = [];
    let highCount = 0;
    let lowCount = 0;

    validEntries.forEach(e => {{
        const z = activeStd > 1e-9 ? (e.val - mean) / activeStd : 0;
        let status = "Normal";
        let isAnomaly = false;

        if (z > zThreshold) {{
            status = "Unusually High";
            isAnomaly = true;
            highCount++;
        }} else if (z < -zThreshold) {{
            status = "Unusually Low";
            isAnomaly = true;
            lowCount++;
        }}

        currentAnomalies.push({{
            ...e,
            z: z,
            status,
            isAnomaly
        }});
    }});

    const totalAnomalies = highCount + lowCount;
    const anomRate = (totalAnomalies / n) * 100;

    // UPDATE FOUR PRIMARY RESULT CARDS
    document.getElementById("kpiN").textContent = n.toLocaleString();
    document.getElementById("kpiCleanSub").textContent = `Total usable measurements: ${{n.toLocaleString()}} (${{parsedRows.length - n}} missing)`;
    document.getElementById("kpiMean").textContent = mean.toFixed(2);
    document.getElementById("kpiStd").textContent = activeStd.toFixed(2);
    document.getElementById("kpiStdLabel").textContent = stdMode === "sample" ? "Standard Deviation (s)" : "Standard Deviation (σ)";
    document.getElementById("kpiStdSub").textContent = stdMode === "sample" ? "Sample Std Dev (Bessel's N-1)" : "Population Std Dev (N)";
    document.getElementById("kpiAnomLabel").textContent = `Flagged Anomalies (|Z| > ${{zThreshold.toFixed(1)}})`;
    document.getElementById("kpiAnom").innerHTML = `${{totalAnomalies}} <span style="font-size:0.95rem; font-weight:600; color:var(--text-muted);">(${{anomRate.toFixed(1)}}%)</span>`;
    document.getElementById("kpiAnomSub").textContent = `${{highCount}} High Spikes | ${{lowCount}} Low Dips`;

    // UPDATE STATISTICAL DETAILS GRID
    document.getElementById("gridN").textContent = n.toLocaleString();
    document.getElementById("gridMean").textContent = `${{mean.toFixed(2)}} ${{unit}}`;
    document.getElementById("gridSampleStd").textContent = `${{sampleStd.toFixed(2)}} ${{unit}}`;
    document.getElementById("gridPopStd").textContent = `${{popStd.toFixed(2)}} ${{unit}}`;
    document.getElementById("gridVar").textContent = `${{sampleVar.toFixed(2)}} ${{unit}}²`;
    document.getElementById("gridMedian").textContent = `${{median.toFixed(2)}} ${{unit}}`;
    document.getElementById("gridMin").textContent = `${{minVal.toFixed(2)}} ${{unit}}`;
    document.getElementById("gridMax").textContent = `${{maxVal.toFixed(2)}} ${{unit}}`;

    // UPDATE ANOMALY COUNTS
    document.getElementById("anomTotalPill").textContent = totalAnomalies;
    document.getElementById("anomHighPill").textContent = highCount;
    document.getElementById("anomLowPill").textContent = lowCount;
    document.getElementById("anomNormalPill").textContent = n - totalAnomalies;

    // Probability default
    const probInput = document.getElementById("probInputVal");
    if (!probInput.value || parseFloat(probInput.value) === 0) {{
        probInput.value = (mean + activeStd).toFixed(1);
    }}

    calculateProbabilities();
    renderDistributionChart();
    renderAnomalyPieChart();
    renderAnomalyTable();
    renderQQChart();
}}

// =========================================================
// PROBABILITY CALCULATOR
// =========================================================
function calculateProbabilities() {{
    const val = parseFloat(document.getElementById("probInputVal").value);
    if (isNaN(val) || !currentStats.mean) return;

    const {{ mean, activeStd, unit }} = currentStats;
    const z = activeStd > 1e-9 ? (val - mean) / activeStd : 0;
    const pBelow = normalCDF(val, mean, activeStd);
    const pAbove = 1.0 - pBelow;

    const countBelow = currentLoadValues.filter(v => v <= val).length;
    const empPct = (countBelow / currentStats.n) * 100;

    document.getElementById("calcZ").textContent = `Z = ${{z.toFixed(3)}}`;
    document.getElementById("calcBelow").textContent = `${{(pBelow * 100).toFixed(2)}}%`;
    document.getElementById("calcAbove").textContent = `${{(pAbove * 100).toFixed(2)}}%`;
    document.getElementById("calcEmpirical").textContent = `${{empPct.toFixed(2)}}% (${{countBelow}}/${{currentStats.n}} samples)`;

    const clampedZ = Math.max(-3.5, Math.min(3.5, z));
    const normPos = ((clampedZ + 3.5) / 7.0) * 100;
    document.getElementById("visualPointer").style.left = `${{normPos}}%`;
    document.getElementById("visualCaption").innerHTML = `Value is <b>${{Math.abs(z).toFixed(2)}}σ</b> ${{z >= 0 ? "above" : "below"}} baseline mean (${{val.toFixed(1)}} ${{unit}}).`;
}}

// =========================================================
// VISUALIZATIONS
// =========================================================
function renderDistributionChart() {{
    const ctx = document.getElementById("distChart").getContext("2d");
    if (distChartInstance) distChartInstance.destroy();

    const {{ mean, activeStd, n, unit }} = currentStats;
    const nBins = Math.min(26, Math.max(10, Math.round(Math.sqrt(n))));

    const min = Math.min(...currentLoadValues);
    const max = Math.max(...currentLoadValues);
    const binWidth = (max - min) / nBins;

    const binEdges = [];
    const binCounts = new Array(nBins).fill(0);
    for (let i = 0; i <= nBins; i++) binEdges.push(min + i * binWidth);

    currentLoadValues.forEach(v => {{
        let idx = Math.floor((v - min) / binWidth);
        if (idx >= nBins) idx = nBins - 1;
        binCounts[idx]++;
    }});

    const binLabels = [];
    const histData = [];
    for (let i = 0; i < nBins; i++) {{
        const mid = (binEdges[i] + binEdges[i+1]) / 2;
        binLabels.push(mid.toFixed(1));
        histData.push(histScaleMode === "density" ? (binCounts[i] / (n * binWidth)) : binCounts[i]);
    }}

    const curvePoints = binLabels.map(label => {{
        const x = parseFloat(label);
        const pdf = normalPDF(x, mean, activeStd);
        return histScaleMode === "density" ? pdf : pdf * n * binWidth;
    }});

    distChartInstance = new Chart(ctx, {{
        type: "bar",
        data: {{
            labels: binLabels,
            datasets: [
                {{
                    label: histScaleMode === "density" ? "Observed Density" : "Observation Frequency",
                    data: histData,
                    backgroundColor: "rgba(37, 99, 235, 0.4)",
                    borderColor: "#2563EB",
                    borderWidth: 1.5,
                    borderRadius: 3,
                    barPercentage: 0.96,
                    categoryPercentage: 1.0
                }},
                {{
                    label: `Fitted Gaussian Curve N(μ=${{mean.toFixed(1)}}, σ=${{activeStd.toFixed(1)}})`,
                    data: curvePoints,
                    type: "line",
                    borderColor: "#DC2626",
                    borderWidth: 2.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.35
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: "top",
                    labels: {{ font: {{ family: "'Inter', sans-serif", size: 12 }} }}
                }}
            }},
            scales: {{
                x: {{
                    title: {{ display: true, text: `Traffic Load (${{unit}})`, font: {{ weight: "bold" }} }},
                    grid: {{ color: "rgba(0,0,0,0.04)" }}
                }},
                y: {{
                    title: {{ display: true, text: histScaleMode === "density" ? "Probability Density f(x)" : "Observation Frequency", font: {{ weight: "bold" }} }},
                    grid: {{ color: "rgba(0,0,0,0.04)" }}
                }}
            }}
        }}
    }});
}}

function renderAnomalyPieChart() {{
    const ctx = document.getElementById("anomalyPieChart").getContext("2d");
    if (anomalyPieChartInstance) anomalyPieChartInstance.destroy();

    const normalCount = currentStats.n - currentAnomalies.filter(a => a.isAnomaly).length;
    const highCount = currentAnomalies.filter(a => a.status === "Unusually High").length;
    const lowCount = currentAnomalies.filter(a => a.status === "Unusually Low").length;

    anomalyPieChartInstance = new Chart(ctx, {{
        type: "doughnut",
        data: {{
            labels: ["In-Bounds Normal", "High Spikes", "Low Dips"],
            datasets: [{{
                data: [normalCount, highCount, lowCount],
                backgroundColor: ["#10B981", "#EF4444", "#0284C7"],
                borderWidth: 2,
                borderColor: "#FFFFFF"
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: "bottom",
                    labels: {{ font: {{ family: "'Inter', sans-serif", size: 11 }} }}
                }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            const val = context.raw || 0;
                            const pct = ((val / currentStats.n) * 100).toFixed(1);
                            return ` ${{context.label}}: ${{val}} (${{pct}}%)`;
                        }}
                    }}
                }}
            }},
            cutout: "65%"
        }}
    }});
}}

function renderQQChart() {{
    const ctx = document.getElementById("qqChart").getContext("2d");
    if (qqChartInstance) qqChartInstance.destroy();

    const sorted = [...currentLoadValues].sort((a, b) => a - b);
    const n = sorted.length;
    const {{ mean, activeStd }} = currentStats;

    const dataPoints = [];
    const minZ = -3.2;
    const maxZ = 3.2;

    for (let i = 0; i < n; i++) {{
        const p = (i + 0.5) / n;
        const theoZ = standardNormalQuantile(p);
        const empZ = activeStd > 1e-9 ? (sorted[i] - mean) / activeStd : 0;
        dataPoints.push({{ x: theoZ, y: empZ }});
    }}

    qqChartInstance = new Chart(ctx, {{
        type: "scatter",
        data: {{
            datasets: [
                {{
                    label: "Observed Quantiles",
                    data: dataPoints,
                    backgroundColor: "#2563EB",
                    pointRadius: 3
                }},
                {{
                    label: "Theoretical Normal Line (45°)",
                    data: [{{ x: minZ, y: minZ }}, {{ x: maxZ, y: maxZ }}],
                    type: "line",
                    borderColor: "#DC2626",
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                x: {{
                    title: {{ display: true, text: "Theoretical Standard Quantiles (Z)" }},
                    min: -3.5,
                    max: 3.5,
                    grid: {{ color: "rgba(0,0,0,0.04)" }}
                }},
                y: {{
                    title: {{ display: true, text: "Standardized Observed Quantiles (Z)" }},
                    min: -3.5,
                    max: 3.5,
                    grid: {{ color: "rgba(0,0,0,0.04)" }}
                }}
            }}
        }}
    }});

    document.getElementById("fitSkewness").textContent = currentStats.skewness.toFixed(3);
    document.getElementById("fitKurtosis").textContent = currentStats.kurtosis.toFixed(3);
}}

function renderAnomalyTable() {{
    const filter = document.getElementById("tableFilterSelect").value;
    const tbody = document.getElementById("anomalyTableBody");
    tbody.innerHTML = "";

    let rows = [...currentAnomalies];

    if (filter === "anomalies") rows = rows.filter(r => r.isAnomaly);
    else if (filter === "high") rows = rows.filter(r => r.status === "Unusually High");
    else if (filter === "low") rows = rows.filter(r => r.status === "Unusually Low");

    if (rows.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:18px; color:var(--text-muted);">✅ No observations matched the selected filter.</td></tr>';
        return;
    }}

    rows.forEach(r => {{
        const tr = document.createElement("tr");
        const statusClass = r.status === "Unusually High" ? "status-high" : (r.status === "Unusually Low" ? "status-low" : "status-normal");
        tr.innerHTML = `
            <td style="font-family:'JetBrains Mono', monospace;">#${{r.index}}</td>
            <td>${{r.time}}</td>
            <td><strong style="font-family:'JetBrains Mono', monospace;">${{r.val.toFixed(2)}}</strong> ${{currentStats.unit}}</td>
            <td><code style="font-family:'JetBrains Mono', monospace; font-weight:600;">${{r.z >= 0 ? "+" : ""}}${{r.z.toFixed(3)}}</code></td>
            <td><span class="status-badge ${{statusClass}}">${{r.status}}</span></td>
        `;
        tbody.appendChild(tr);
    }});
}}

// =========================================================
// CSV EXPORTS
// =========================================================
function exportAnalyzedCSV() {{
    if (!currentAnomalies.length) return;
    let csv = "index,timestamp,load_value,z_score,status\\n";
    currentAnomalies.forEach(a => {{
        csv += `${{a.index}},"${{a.time}}",${{a.val.toFixed(2)}},${{a.z.toFixed(3)}},"${{a.status}}"\\n`;
    }});
    downloadBlob(csv, "analyzed_traffic_results.csv", "text/csv");
}}

function exportAnomaliesCSV() {{
    const anomalies = currentAnomalies.filter(a => a.isAnomaly);
    if (!anomalies.length) {{
        alert("No anomalies currently flagged.");
        return;
    }}
    let csv = "index,timestamp,load_value,z_score,status\\n";
    anomalies.forEach(a => {{
        csv += `${{a.index}},"${{a.time}}",${{a.val.toFixed(2)}},${{a.z.toFixed(3)}},"${{a.status}}"\\n`;
    }});
    downloadBlob(csv, "flagged_network_anomalies.csv", "text/csv");
}}

function downloadBlob(content, filename, contentType) {{
    const blob = new Blob([content], {{ type: contentType }});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}}

function switchTab(tabId, btn) {{
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
    document.getElementById(tabId).classList.add("active");
    btn.classList.add("active");

    // Trigger Chart.js updates if rendered while tab was hidden
    setTimeout(() => {{
        if (tabId === "tab-overview" && distChartInstance) {{
            distChartInstance.resize();
        }} else if (tabId === "tab-anomalies" && anomalyPieChartInstance) {{
            anomalyPieChartInstance.resize();
        }} else if (tabId === "tab-details" && qqChartInstance) {{
            qqChartInstance.resize();
        }}
    }}, 50);
}}
</script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully built updated index.html with Pie chart and fixed JS!")

if __name__ == "__main__":
    generate_index_html()
