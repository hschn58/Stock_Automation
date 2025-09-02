# Stock Anomaly Heatmap Generator

A desktop GUI (Tkinter) for spotting **ticker-specific deviations** from a chosen baseline over flexible time ranges.  
The app fetches prices from Yahoo Finance, computes smoothed percent-change series, and visualizes **deviations from the basket average or a selected baseline stock** as a time-aligned heatmap.

![Screenshot](./Stock_Comparison_Output.png)

> **Note**: All configuration (tickers, time period, baseline) is done in the GUI—no command-line flags.

---

## Features

- **Point-and-click ticker list** (add/remove; `Delete` key removes selected).
- **Flexible time window**: X days / months / years.
- **Baseline options**:
  - *Default (basket mean)* – average of all selected tickers.
  - *Specific stock* – deviations relative to one chosen ticker.
- **Adaptive intraday handling** based on your time range:
  - ≤ 7 days → 1-minute data  
  - ≤ 60 days → 5-minute data  
  - ≤ ~2 years → 1-hour data  
  - Longer → daily data
- **Smoothing & signal highlighting**:
  - Gaussian smoothing on both baseline and tickers.
  - Centered moving average (≈10% of series length).
  - Red/blue overlays emphasize stronger positive/negative deviations.
- **Readable axis**: date-only x-labels (time-of-day removed).
- **No API keys** required.

---

## Installation

### Requirements
- Python 3.10+
- Works on macOS, Windows, Linux (Tkinter GUI).

### Install dependencies

Install required packages manually:

```bash
pip install yfinance pandas numpy scipy matplotlib requests
```

## Run

From this folder:

```bash
python stock_anomaly_heatmap.py
```

Replace `stock_anomaly_heatmap.py` with your actual script name if different.

---

## How to Use

- **Choose Time Period**  
  Enter a number (e.g., `10`) and select units (`days`, `months`, `years`).

- **Add Tickers**  
  Type a ticker symbol (e.g., `NVDA`, `AMD`, `AVGO`) and click **Add**.  
  Use **Remove Selected** or the `Delete` key to remove.

- **Select Baseline**
  - *Default (basket mean)* – average of all tickers.
  - *Specific stock* – baseline is one ticker you select.

- **Generate**  
  Click **Generate Heatmap** to fetch data and view results.

---

## Methodology

- **Data fetch**: Adjusted close (or close) from Yahoo Finance.  
- **Percent change**: Each ticker converted to `pct_change()`.  
- **Baseline**: Basket mean or user-selected stock.  
- **Smoothing**:  
  - Gaussian filter (σ = 1) for baseline and tickers.  
  - Centered moving average (≈10% of series length).  
- **Deviation calculation**:  
  `Deviation = Smoothed(ticker %Δ) – Smoothed(baseline %Δ)`  
- **Color scale**:  
  - Diverging seismic colormap centered at 0.  
  - Limits set from 2nd–98th percentile of all deviations.  
- **Highlight overlay**:  
  Regions above thresholds emphasized (adaptive: 0.5% intraday, 1% hourly, 3% daily).

---

## Interpretation

- 🔴 **Red** = outperformance vs. baseline  
- 🔵 **Blue** = underperformance vs. baseline  

---

## Tips & Notes

- **Yahoo intraday limits**:  
  - ≤ 7 days → 1-minute bars  
  - ≤ 60 days → 5-minute bars  
  - ≤ 730 days → 1-hour bars  
  - Longer → daily bars  

- Date-only labels: X-axis strips time-of-day for clarity.  
- Retries: Built-in retry with exponential backoff.  
- Session headers: Uses a persistent HTTP session for stability.  

---

## Troubleshooting

- **Invalid Ticker**: Only A–Z, 0–9, `.`, and `-` are allowed.  
- **Empty chart**: Try a longer window or different tickers.  
- **Tkinter errors**: Install the system’s Tk package if missing.  

---

## Folder Structure

```
Stock_Comparison/
├── stock_anomaly_heatmap.py      # main GUI script
├── Stock_Comparison_Output.png   # screenshot for README
```

---

## License

MIT (or your chosen license).

---

## Disclaimer

This software is provided for informational and educational purposes only.  
It does not constitute financial advice or a recommendation to trade securities.
