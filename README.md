# Stock Automation

A collection of Python tools and lightweight apps for automating financial data tasks: fetching fundamentals, screening anomalies, comparing tickers, and generating charts.  
Designed for quick research workflows and client-facing outputs.

---

## Repository Structure

- **Stock_Drops/**  
  Tkinter GUI for anomaly detection. Fetches intraday % moves, builds a heatmap of deviations vs. peers, highlights cells ≥ ±3%, and flags strong conditions.

- **Company_Financials/**  
  Scripts to pull dividends, earnings dates, payout ratios, and simple statement snapshots.

- **Stock_Comparison/**  
  Utilities for pairwise and basket analysis (correlations, rolling returns, beta-like metrics).

- **Client_Performance_Chart/**  
  Generates performance charts suitable for client presentation.

- **Client_Portfolio_Filter/**  
  Cleans and filters portfolio exports (exclude cash, collapse classes, fix tickers).

- **Client_Summary_Acquisition/**  
  Quickly assembles account or holdings summaries from raw custodial exports.

- **Methods/**  
  Shared helper functions (date/time, I/O, plotting, error handling).

---

## Quickstart

### 1. Environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -U pip
```

---

## License

This project is licensed under the [MIT License](../LICENSE).

---

## Disclaimer
This repository is not an attempt to solicit financial advice.

This software is provided for informational and educational purposes only.  
It does not constitute financial advice or a recommendation to trade securities.


