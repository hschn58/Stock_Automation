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


## Run

From this folder:

\begin{verbatim}
python stock_anomaly_heatmap.py
\end{verbatim}

Replace \texttt{stock_anomaly_heatmap.py} with your actual script name if different.

---

## How to Use

\begin{itemize}
  \item \textbf{Choose Time Period} \\
        Enter a number (e.g., 10) and select units (days, months, years).

  \item \textbf{Add Tickers} \\
        Type a ticker symbol (e.g., NVDA, AMD, AVGO) and click \textbf{Add}. \\
        Use \textbf{Remove Selected} or the Delete key to remove.

  \item \textbf{Select Baseline} 
        \begin{itemize}
          \item Default (basket mean) – average of all tickers.
          \item Specific stock – baseline is one ticker you select.
        \end{itemize}

  \item \textbf{Generate} \\
        Click \textbf{Generate Heatmap} to fetch data and view results.
\end{itemize}

---

## Methodology

\begin{itemize}
  \item \textbf{Data fetch}: Adjusted close (or close) from Yahoo Finance.
  \item \textbf{Percent change}: Each ticker converted to \texttt{pct\_change()}.
  \item \textbf{Baseline}: Basket mean or user-selected stock.
  \item \textbf{Smoothing}:
    \begin{itemize}
      \item Gaussian filter ($\sigma=1$) for baseline and tickers.
      \item Centered moving average ($\approx 10\%$ of series length).
    \end{itemize}
  \item \textbf{Deviation calculation}: \\
        $Deviation = Smoothed(\Delta ticker) - Smoothed(\Delta baseline)$
  \item \textbf{Color scale}:
    \begin{itemize}
      \item Diverging seismic colormap centered at 0.
      \item Limits set from 2nd--98th percentile of all deviations.
    \end{itemize}
  \item \textbf{Highlight overlay}: \\
        Regions above thresholds emphasized 
        (adaptive: 0.5\% intraday, 1\% hourly, 3\% daily).
\end{itemize}

---

## Interpretation

- 🔴 \textbf{Red} = outperformance vs. baseline  
- 🔵 \textbf{Blue} = underperformance vs. baseline  

---

## Tips \& Notes

- \textbf{Yahoo intraday limits}:  
  \begin{itemize}
    \item $\leq 7$ days $\rightarrow$ 1-minute bars
    \item $\leq 60$ days $\rightarrow$ 5-minute bars
    \item $\leq 730$ days $\rightarrow$ 1-hour bars
    \item Longer $\rightarrow$ daily bars
  \end{itemize}

- Date-only labels: X-axis strips time-of-day for clarity.  
- Retries: Built-in retry with exponential backoff.  
- Session headers: Uses a persistent HTTP session for stability.  

---

## Troubleshooting

- \textbf{Invalid Ticker}: Only A--Z, 0--9, ., and - are allowed.  
- \textbf{Empty chart}: Try a longer window or different tickers.  
- \textbf{Tkinter errors}: Install the system’s Tk package if missing.  

---

## Folder Structure

\begin{verbatim}
Stock_Comparison/
├── stock_anomaly_heatmap.py      # main GUI script
├── Stock_Comparison_Output.png   # screenshot for README
\end{verbatim}

---

## License

MIT (or your chosen license).

---

## Disclaimer

This software is provided for informational and educational purposes only.  
It does not constitute financial advice or a recommendation to trade securities.

