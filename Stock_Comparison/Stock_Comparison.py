

import tkinter as tk
from tkinter import messagebox, ttk
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from datetime import datetime, timedelta
import re
import requests
import time
import logging
from io import BytesIO
import base64

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

class StockApp:
    def __init__(self, root):
        self.root = root
        self.dev_threshold = 0.03  # 3% threshold for deviations
        self.root.title("Stock Anomaly Heatmap Generator")

        # One shared session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0.0.0 Safari/537.36"),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })

        # ---- Controls ----
        tk.Label(root, text="Time Period:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.time_num = tk.Entry(root, validate="key", width=8)
        self.time_num['validatecommand'] = (root.register(self.validate_num), '%P')
        self.time_num.grid(row=0, column=1, sticky="w")
        self.time_num.insert(0, "10")

        self.time_unit = ttk.Combobox(root, values=["days", "months", "years"], state="readonly", width=8)
        self.time_unit.current(0)
        self.time_unit.grid(row=0, column=2, sticky="w")

        # Baseline selector
        tk.Label(root, text="Baseline:").grid(row=0, column=3, padx=(20,4), sticky="e")
        self.baseline_mode_var = tk.StringVar(value="Default (basket mean)")
        self.baseline_mode = ttk.Combobox(
            root,
            textvariable=self.baseline_mode_var,
            state="readonly",
            values=["Default (basket mean)", "Specific stock"],
            width=20
        )
        self.baseline_mode.grid(row=0, column=4, sticky="w")
        self.baseline_mode.bind("<<ComboboxSelected>>", lambda e: self._toggle_baseline_stock())

        self.baseline_stock_var = tk.StringVar(value="")
        self.baseline_stock = ttk.Combobox(root, textvariable=self.baseline_stock_var, state="disabled", width=10)
        self.baseline_stock.grid(row=0, column=5, sticky="w", padx=(6,0))

        # Add/remove tickers
        tk.Label(root, text="Add Ticker:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ticker_entry = tk.Entry(root, width=14)
        self.ticker_entry.grid(row=1, column=1, sticky="w")
        tk.Button(root, text="Add", command=self.add_ticker, width=8).grid(row=1, column=2, sticky="w", padx=(6,0))
        tk.Button(root, text="Remove Selected", command=self.remove_selected, width=16)\
            .grid(row=1, column=4, columnspan=2, sticky="w", padx=(10,0))

        # Stock list
        self.stock_list = tk.Listbox(root, height=10, width=22, selectmode=tk.EXTENDED, exportselection=False)
        self.stock_list.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        self.stocks = []
        self.stock_list.bind("<Delete>", lambda e: self.remove_selected())

        # Generate button
        tk.Button(root, text="Generate Heatmap", command=self.generate_heatmap).grid(
            row=3, column=0, columnspan=3, pady=10
        )

        # Plot area
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.grid(row=4, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        self.canvas = None
        self.toolbar = None
        self.img_label = None
        self._img_ref = None

        self.dpi = 150
        self.row_px = 28
        self.min_row_px = 12

    def _toggle_baseline_stock(self):
        use_stock = (self.baseline_mode_var.get() == "Specific stock")
        self.baseline_stock.configure(state=("readonly" if use_stock else "disabled"))

    def _refresh_baseline_choices(self):
        # keep choices in sync with current stocks
        self.baseline_stock['values'] = list(self.stocks) if self.stocks else []
        if self.baseline_stock_var.get() not in self.stocks:
            self.baseline_stock_var.set(self.stocks[0] if self.stocks else "")

    def validate_num(self, value):
        return value.isdigit() or value == ""

    def fetch_with_retry(self, symbol, tries=3, pause=0.8, **kwargs):
        sym = re.sub(r"^\$+", "", (symbol or "").strip().upper())
        last_err = None
        for attempt in range(1, tries + 1):
            try:
                df = self._fetch_chart_direct(sym, **kwargs)
                if df is not None and not df.empty:
                    return df
                t = yf.Ticker(sym, session=self.session)
                hist = t.history(**kwargs) if kwargs else t.history(period="5d", interval="1d")
                if hist is not None and not hist.empty:
                    return hist
                last_err = ValueError("No data returned")
            except Exception as e:
                last_err = e
            time.sleep(pause * attempt)
        raise last_err

    def _fetch_chart_direct(self, symbol, period=None, interval="1d", start=None, end=None):
        import time as _time
        import pandas as _pd
        base = "https://query1.finance.yahoo.com/v8/finance/chart/"
        params = {"interval": interval, "includeAdjustedClose": "true", "events": "div,splits"}
        if period is not None:
            params["range"] = str(period)
        else:
            def _to_epoch(x):
                if x is None: return None
                if isinstance(x, (int, float)): return int(x)
                ts = _pd.to_datetime(x); return int(ts.timestamp())
            params["period1"] = _to_epoch(start) if start is not None else 0
            params["period2"] = _to_epoch(end) if end is not None else int(_time.time())
        r = self.session.get(base + symbol, params=params, timeout=12)
        ctype = r.headers.get("content-type", "")
        if "json" not in ctype.lower():
            snippet = (r.text or "")[:120].replace("\n", " ")
            raise ValueError(f"Yahoo returned non-JSON ({ctype}): {snippet!r}")
        data = r.json()
        ch = data.get("chart", {})
        if ch.get("error"):
            desc = ch["error"].get("description") or str(ch["error"])
            raise ValueError(f"Yahoo chart error: {desc}")
        results = ch.get("result") or []
        if not results:
            raise ValueError("Yahoo chart: empty result")
        res = results[0]
        ts = res.get("timestamp") or []
        if not ts:
            raise ValueError("Yahoo chart: no timestamps")
        ind = res.get("indicators", {})
        q = (ind.get("quote") or [{}])[0]
        adj = (ind.get("adjclose") or [{}])[0].get("adjclose")
        df = _pd.DataFrame({
            "Open":   q.get("open"),
            "High":   q.get("high"),
            "Low":    q.get("low"),
            "Close":  q.get("close"),
            "Adj Close": adj if adj is not None else q.get("close"),
            "Volume": q.get("volume"),
        }, index=_pd.to_datetime(ts, unit="s", utc=True))
        tz = (res.get("meta") or {}).get("timezone")
        if tz and isinstance(df.index, _pd.DatetimeIndex):
            try: df.index = df.index.tz_convert(tz).tz_localize(None)
            except Exception: df.index = df.index.tz_localize(None)
        else:
            if getattr(df.index, "tz", None):
                df.index = df.index.tz_localize(None)
        return df.dropna(how="all")

    def add_ticker(self):
        raw = self.ticker_entry.get().strip()
        ticker = re.sub(r"^\$+", "", raw).upper()
        if not re.match(r'^[A-Z0-9.\-]+$', ticker):
            messagebox.showerror("Invalid Input", "Ticker must be A–Z, 0–9, dot, or hyphen.")
            return
        if ticker in self.stocks:
            messagebox.showerror("Duplicate", "Ticker already added.")
            return
        try:
            df = self.fetch_with_retry(ticker, period="5d", interval="1d")
            if df is None or df.empty:
                raise ValueError("Data empty")
            self.stocks.append(ticker)
            self.stock_list.insert(tk.END, ticker)
            self.ticker_entry.delete(0, tk.END)
            self._refresh_baseline_choices()
        except Exception as e:
            messagebox.showerror(
                "Invalid Ticker",
                f"{ticker} does not exist or data unavailable.\nError: {str(e)}"
            )

    def remove_selected(self):
        sel = list(self.stock_list.curselection())
        if not sel:
            messagebox.showwarning("No Selection", "Select one or more tickers to remove.")
            return
        for idx in reversed(sel):
            ticker = self.stock_list.get(idx)
            try: self.stocks.remove(ticker)
            except ValueError: pass
            self.stock_list.delete(idx)
        self._refresh_baseline_choices()

    def generate_heatmap(self):
        if not self.stocks:
            messagebox.showerror("No Stocks", "Add at least one stock.")
            return
        num = self.time_num.get()
        if not num:
            messagebox.showerror("Invalid Time", "Enter a number.")
            return
        num = int(num)
        unit = self.time_unit.get()
        if unit == "days":
            delta = timedelta(days=num)
        elif unit == "months":
            delta = timedelta(days=num * 30)
        else:
            delta = timedelta(days=num * 365)
        start = datetime.now() - delta

        # Intraday-friendly ranges
        if delta <= timedelta(days=7):
            fetch_args = dict(period="7d", interval="1m")
        elif delta <= timedelta(days=60):
            fetch_args = dict(period="60d", interval="5m")
        elif delta <= timedelta(days=730):
            fetch_args = dict(period="730d", interval="1h")
        else:
            fetch_args = dict(start=start, interval="1d")
        interval = fetch_args["interval"]

        # Fetch
        data_dict = {}
        for ticker in self.stocks:
            try:
                df = self.fetch_with_retry(ticker, **fetch_args)
                if df is None or df.empty:
                    raise ValueError("Data empty")
                if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
                    df = df.copy(); df.index = df.index.tz_localize(None)
                price_col = "Adj Close" if "Adj Close" in df.columns else ("Close" if "Close" in df.columns else None)
                if price_col is None:
                    raise KeyError("No price column in data")
                series = df[price_col].pct_change().dropna()
                data_dict[ticker] = series
            except Exception as e:
                messagebox.showerror("Data Error", f"Failed to fetch data for {ticker}.\nError: {str(e)}")
                return

        if not data_dict:
            messagebox.showerror("Data Error", "No data available.")
            return

        # Align into DataFrame of pct changes
        all_times = pd.concat(list(data_dict.values())).index.unique().sort_values()
        pct_changes = pd.DataFrame({t: data_dict[t].reindex(all_times).fillna(0) for t in self.stocks})

        # ---- Choose baseline: basket mean (default) or specific stock ----
        use_stock = (self.baseline_mode_var.get() == "Specific stock")
        chosen = self.baseline_stock_var.get()
        if use_stock and chosen in pct_changes.columns:
            baseline_pct = pct_changes[chosen]
        else:
            baseline_pct = pct_changes.mean(axis=1)

        # Smooth baseline and each stock, then deviations vs. baseline
        baseline_smoothed = pd.Series(gaussian_filter1d(baseline_pct.to_numpy(), sigma=1), index=baseline_pct.index)

        deviations = {}
        for t in self.stocks:
            stock_smoothed = pd.Series(gaussian_filter1d(pct_changes[t].to_numpy(), sigma=1),
                                       index=pct_changes.index)
            deviations[t] = stock_smoothed - baseline_smoothed

        # Moving-average window = 10% of available points (centered), odd-sized.
        def _ma_window_for_length(n: int) -> int:
            if n <= 0: return 5
            w = max(5, int(round(0.10 * n)))
            w = min(w, n)
            if w % 2 == 0: w = max(5, w - 1)
            return w

        deviations_ma = {}
        N = len(pct_changes.index)
        win = _ma_window_for_length(N)
        for t, s in deviations.items():
            deviations_ma[t] = s.rolling(window=win, center=True, min_periods=max(1, win // 3)).mean()

        # Global normalization
        all_devs = np.concatenate([v.to_numpy() for v in deviations_ma.values()])
        lo = np.nanpercentile(all_devs, 2)
        hi = np.nanpercentile(all_devs, 98)
        m = max(abs(lo), abs(hi), 1e-6)
        norm = TwoSlopeNorm(vmin=-m, vcenter=0.0, vmax=m)

        # Threshold scaling for intraday
        threshold = self.dev_threshold
        if interval in ('1m', '2m', '5m', '15m', '30m'):
            threshold = min(threshold, 0.005)
        elif interval in ('60m', '90m', '1h'):
            threshold = min(threshold, 0.01)

        # ---- Plot ----
        rows = len(self.stocks)
        try: self.root.update_idletasks()
        except Exception: pass
        frame_w = self.plot_frame.winfo_width() or 800
        frame_h = self.plot_frame.winfo_height() or 420
        dpi        = getattr(self, 'dpi', 150)
        row_px     = getattr(self, 'row_px', 36)
        min_row_px = getattr(self, 'min_row_px', 16)
        avail_h = max(220, frame_h - 80)
        if rows * row_px > avail_h:
            row_px = max(min_row_px, avail_h // max(1, rows))
        fig_w_in = frame_w / dpi
        fig_h_in = max(rows * row_px + 50, 200) / dpi

        fig, axs = plt.subplots(rows, 1, figsize=(fig_w_in, fig_h_in),
                                sharex=True, constrained_layout=False,
                                gridspec_kw={'hspace': 0})
        axs = np.atleast_1d(axs)

        # --- date-only labels (no time-of-day) ---
        date_index = baseline_smoothed.index.normalize()          # strip time-of-day
        time_labels = date_index.strftime('%Y-%m-%d')


        for i, t in enumerate(self.stocks):
            dev_trend = deviations_ma[t].to_numpy()

            axs[i].imshow([dev_trend], cmap='seismic', aspect='auto', norm=norm,
                          interpolation='nearest', alpha=0.65)

            signed_mask = np.where(dev_trend >= threshold, 1.0,
                            np.where(dev_trend <= -threshold, -1.0, 0.0))
            hit_ix = np.flatnonzero(signed_mask)
            Np = dev_trend.size
            if hit_ix.size:
                if hit_ix.size >= 2:
                    med_gap = np.median(np.diff(hit_ix))
                    sigma_hits = float(np.clip(med_gap / 2.0, 2.0, max(3.0, Np/6)))
                else:
                    sigma_hits = max(3.0, Np / 24.0)
                from scipy.ndimage import gaussian_filter1d as _gf1d
                glow = _gf1d(signed_mask, sigma=sigma_hits)
                overlay_alpha = np.clip(np.abs(glow) * 1.25, 0.0, 0.9).reshape(1, -1)
                overlay_values = (0.8 * m) * np.sign(glow) * np.clip(np.abs(glow), 0.0, 1.0)
                axs[i].imshow([overlay_values], cmap='seismic', aspect='auto', norm=norm,
                              interpolation='nearest', alpha=overlay_alpha)

            # cosmetics
            axs[i].set_yticks([])
            axs[i].set_ylabel(t, rotation=0, ha='right', va='center', fontsize=10, labelpad=10)
            axs[i].tick_params(axis='y', length=0)
            for s in ('top','right','left','bottom'):
                axs[i].spines[s].set_visible(False)
            if i < rows - 1:
                axs[i].set_xticks([])

        # right-side colorbar in free space
        import matplotlib.ticker as mticker
        from matplotlib.cm import ScalarMappable
        sm = ScalarMappable(cmap='seismic', norm=norm); sm.set_array([])

        left, right, top, bottom = 0.18, 1.06, 0.98, 0.20
        fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)

        gap = 0.01
        cb_width = 0.04
        cb_left   = right + gap
        cb_bottom = bottom
        cb_height = top - bottom
        cb_ax = fig.add_axes([cb_left, cb_bottom, cb_width, cb_height])
        cb = plt.colorbar(sm, cax=cb_ax, orientation='vertical')
        cb.formatter = mticker.FuncFormatter(lambda x, pos: f"{x*100:.2f}%")
        cb.update_ticks()
        cb.set_label("Deviation from average (%)", fontsize=9)

        n = len(time_labels)
        if n:
            positions = np.linspace(0, n - 1, min(10, n)).astype(int)
            axs[-1].set_xticks(positions)
            axs[-1].set_xticklabels([time_labels[j] for j in positions],
                                    rotation=45, ha='right', fontsize=8)

        # final margin tweak
        fig.subplots_adjust(left=0.18, right=0.92, top=0.98, bottom=0.20)
        self._render_figure(fig)

    def _render_figure(self, fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        try:
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            img = tk.PhotoImage(data=b64)
        except tk.TclError:
            try:
                from PIL import Image, ImageTk
                buf.seek(0)
                pil_img = Image.open(buf)
                img = ImageTk.PhotoImage(pil_img)
            except Exception as e:
                messagebox.showerror("Display Error", f"Could not render image in Tk: {e}")
                return
        if self.img_label is None:
            self.img_label = tk.Label(self.plot_frame)
            self.img_label.grid(row=0, column=0, sticky="nsew")
        self.img_label.configure(image=img)
        self._img_ref = img

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
