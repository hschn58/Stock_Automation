#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
import re
from io import BytesIO
import openpyxl  # keep writer backend available #tksheet 

# Try to use tksheet for per-cell coloring; fallback to Treeview
try:
    import tksheet
    HAS_TKSHEET = True
except Exception:
    HAS_TKSHEET = False

DEFAULT_TICKERS = [
    'HD','HON','LMT','WSM','CLX','COST','GIS','MKC','PEP','BLK','ICE','JPM','PYPL','USB','ABT',
    'AMGN','BMY','MRK','TMO','UNH','JNJ','WM','AAPL','AMZN','META','GOOG','MSFT','ADBE','ANET',
    'CSCO','EBAY','ORCL','TXN','CNI','UNP','UPS','NEE','DUK','AMT','DLR','O'
]

PCT_DROP_THRESHOLD_SOFT = -3.0
PCT_DROP_THRESHOLD_STRONG = -6.0

PCT_RISE_THRESHOLD_SOFT   =  3.0
PCT_RISE_THRESHOLD_STRONG =  6.0

HORIZONS = [(5, "Five Days"), (4, "Four Days"), (3, "Three Days")]

import requests

# one shared session helps with Yahoo quirks
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
})

# 101 --- Direct Yahoo "chart" fetch (bypasses yfinance) ------------------------
def _fetch_chart_direct(symbol, period="15d", interval="1d", start=None, end=None, session=None, timeout=12):
    """
    Return a tidy OHLCV DataFrame using Yahoo Finance v8 chart API.
    Prefers range=period when provided; otherwise uses period1/period2.
    Index is tz-naive local market time (for consistency with the rest of the app).
    """
    import time as _time
    import pandas as _pd

    sess = session or _SESSION
    base = "https://query1.finance.yahoo.com/v8/finance/chart/"
    params = {
        "interval": interval,
        "includeAdjustedClose": "true",
        "events": "div,splits",
    }

    if period is not None:
        # e.g. "15d", "1mo" etc.
        params["range"] = str(period)
    else:
        def _to_epoch(x):
            if x is None: return None
            if isinstance(x, (int, float)): return int(x)
            ts = _pd.to_datetime(x); return int(ts.timestamp())
        params["period1"] = _to_epoch(start) if start is not None else 0
        params["period2"] = _to_epoch(end) if end is not None else int(_time.time())

    r = sess.get(base + symbol, params=params, timeout=timeout)
    ctype = r.headers.get("content-type", "")
    if "json" not in ctype.lower():
        snippet = (r.text or "")[:140].replace("\n", " ")
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

    # Convert to market timezone if provided, then strip tz (keep app’s naive index convention)
    tz = (res.get("meta") or {}).get("timezone")
    if tz and isinstance(df.index, _pd.DatetimeIndex):
        try:
            df.index = df.index.tz_convert(tz).tz_localize(None)
        except Exception:
            df.index = df.index.tz_localize(None)
    else:
        if getattr(df.index, "tz", None):
            df.index = df.index.tz_localize(None)

    return df.dropna(how="all")


def _safe_history(ticker, period="15d", interval="1d"):
    """Try Yahoo v8 chart fetch first; if empty/fails, fall back to yfinance. Return tidy OHLCV DF or None."""
    # --- Primary: direct chart API
    try:
        df = _fetch_chart_direct(ticker, period=period, interval=interval, session=_SESSION)
        if df is None or df.empty:
            # fallback to a slightly longer range before giving up
            df = _fetch_chart_direct(ticker, period="1mo", interval="1d", session=_SESSION)
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"[fetch-direct] {ticker}: {e}")

    # --- Secondary: yfinance (quiet fallback)
    try:
        t = yf.Ticker(ticker, session=_SESSION)
        df = t.history(period=period, interval=interval, auto_adjust=False, actions=False)
        if df is None or df.empty:
            df = t.history(period="1mo", interval="1d", auto_adjust=False, actions=False)
        if df is not None and not df.empty:
            if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
                df = df.copy(); df.index = df.index.tz_localize(None)
            return df
    except Exception as e:
        print(f"[fetch-yf] {ticker}: {e}")

    return None


def fetch_stock_data(tickers):
    """Return (Five_Days, Four_Days, Three_Days) restricted to last ~2 weeks, no all-NaN rows."""
    # 1) fetch only good tickers
    close_cols = []
    for t in tickers:
        df = _safe_history(t, period="15d", interval="1d")  # ~10 biz days, enough for 5-day diffs
        if df is None or df.empty:
            continue
        col = None
        if "Close" in df.columns:
            col = df["Close"].rename(t)
        elif "Adj Close" in df.columns:
            col = df["Adj Close"].rename(t)
        if col is not None and not col.dropna().empty:
            close_cols.append(col)

    if not close_cols:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # 2) build closing price matrix and compute % changes
    Closing_Price = pd.concat(close_cols, axis=1).sort_index()

    Percent_Change1 = (Closing_Price / Closing_Price.shift(5) - 1) * 100  # 5-day
    Percent_Change2 = (Closing_Price / Closing_Price.shift(4) - 1) * 100  # 4-day
    Percent_Change3 = (Closing_Price / Closing_Price.shift(3) - 1) * 100  # 3-day

    # 3) restrict *display* to the last 14 calendar days (≈ two trading weeks)
    def _window(df, days=14):
        if df is None or df.empty:
            return df
        last = df.index.max()
        cutoff = last - pd.Timedelta(days=days)
        return df.loc[df.index >= cutoff]

    Percent_Change1 = _window(Percent_Change1)
    Percent_Change2 = _window(Percent_Change2)
    Percent_Change3 = _window(Percent_Change3)

    def _prep_show_all(df):
        """
        Keep all percent changes (rounded), drop rows that are entirely NaN,
        and format Date as YYYY-MM-DD for display.
        """
        if df is None or df.empty:
            return df
        # drop rows where *all* ticker cells are NaN (typical at the very top)
        df = df.dropna(how="all")
        if df.empty:
            return df
        out = df.round(3).reset_index().rename(columns={"index": "Date"})
        out["Date"] = pd.to_datetime(out["Date"], errors="coerce").dt.date.astype(str)
        return out

    # 4) prep for UI (show all pct changes, highlight via colorize_cells)
    Five_Days  = _prep_show_all(Percent_Change1)
    Four_Days  = _prep_show_all(Percent_Change2)
    Three_Days = _prep_show_all(Percent_Change3)
    return Five_Days, Four_Days, Three_Days


def format_dataframe(df):
    if df is None or df.empty:
        return df
    df_copy = df.copy()
    df_copy = df_copy.fillna(0)
    # Avoid applymap deprecation: keep zeros as ints for display
    for c in df_copy.columns:
        if c == "Date":
            continue
        try:
            df_copy[c] = pd.to_numeric(df_copy[c], errors="ignore")
            df_copy[c] = df_copy[c].where(df_copy[c] != 0, 0).astype(object)
        except Exception:
            pass
    return df_copy



def df_latest_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    From a 'wide' drops DataFrame (with a 'Date' column and tickers as columns),
    return only the latest date’s row. If empty or malformed, return an empty DF
    with the same columns for UI consistency.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=getattr(df, "columns", []))

    if "Date" not in df.columns:
        return pd.DataFrame(columns=df.columns)

    # Find the most recent date present (robust to string format)
    dates = pd.to_datetime(df["Date"], errors="coerce")
    if dates.isna().all():
        return pd.DataFrame(columns=df.columns)

    last_day = dates.max()
    out = df.loc[dates == last_day].copy()

    # If multiple rows share the same date, keep the last (chronological order already in df)
    if len(out) > 1:
        out = out.tail(1)

    # Reindex to 0.. for cleaner display in tksheet/Treeview
    return out.reset_index(drop=True)

# -------------------- Table abstraction --------------------

class Table:
    """Abstraction over tksheet (preferred) or ttk.Treeview (fallback)."""

    def __init__(self, parent):
        self.container = ttk.Frame(parent)
        self.container.pack(expand=True, fill=tk.BOTH)

        if HAS_TKSHEET:
            self.widget = tksheet.Sheet(self.container)
            self.widget.enable_bindings((
                "single_select", "row_select", "column_width_resize", "arrowkeys",
                "rc_select", "rc_insert_row", "rc_delete_row", "copy"
            ))
            self.widget.grid(row=0, column=0, sticky="nsew")
            self.container.columnconfigure(0, weight=1)
            self.container.rowconfigure(0, weight=1)
            self.kind = "sheet"
        else:
            # Fallback to Treeview (row-level coloring only)
            self.widget = ttk.Treeview(self.container, columns=[], show="headings")
            vsb = ttk.Scrollbar(self.container, orient="vertical", command=self.widget.yview)
            hsb = ttk.Scrollbar(self.container, orient="horizontal", command=self.widget.xview)
            self.widget.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            self.widget.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")
            self.container.columnconfigure(0, weight=1)
            self.container.rowconfigure(0, weight=1)
            self.kind = "tree"

    def set_dataframe(self, df: pd.DataFrame):
        if self.kind == "sheet":
            if df is None or df.empty:
                self.widget.set_sheet_data([])
                self.widget.headers([])
                self.widget.set_all_cell_sizes_to_text()
                self.widget.refresh()
                return
            cols = list(df.columns)
            data = df.fillna("").astype(str).values.tolist()
            self.widget.set_sheet_data(data)
            self.widget.headers(cols)
            self.widget.set_all_cell_sizes_to_text()
            self.widget.refresh()
        else:
            # Treeview fallback
            self.widget.delete(*self.widget.get_children())
            if df is None or df.empty:
                self.widget["columns"] = []
                return
            cols = list(df.columns)
            self.widget["columns"] = cols
            for c in cols:
                self.widget.heading(c, text=c)
                self.widget.column(c, width=max(90, int(900 / max(1, len(cols)))))
            for _, row in df.iterrows():
                values = [row.get(c, "") for c in cols]
                # Tag whole row red if any cell meets threshold (coarse fallback)
                tag = ""
                for c in cols:
                    if c == "Date":
                        continue
                    try:
                        v = float(row[c])
                        if v <= PCT_DROP_THRESHOLD_SOFT:
                            tag = "soft"
                        if v <= PCT_DROP_THRESHOLD_STRONG:
                            tag = "strong"
                            break
                    except Exception:
                        pass
                self.widget.insert("", "end", values=values, tags=(tag,))
            self.widget.tag_configure("soft", background="#adffac")
            self.widget.tag_configure("strong", background="#15ff21")

    def colorize_cells(self, df: pd.DataFrame):
        """Only meaningful for tksheet (per-cell)."""
        if self.kind != "sheet" or df is None or df.empty:
            return

        # Clear prior highlights (handle different tksheet versions gracefully)
        try:
            if hasattr(self.widget, "dehighlight_all"):
                self.widget.dehighlight_all()
            elif hasattr(self.widget, "delete_highlighted_cells"):
                self.widget.delete_highlighted_cells()
        except Exception:
            pass

        headers = list(df.columns)
        date_col_idx = headers.index("Date") if "Date" in headers else -1

        # Add highlights cell-by-cell (batch redraw at the end)
        for r_idx in range(len(df)):
            for c_idx, col in enumerate(headers):
                if c_idx == date_col_idx:
                    continue
                val = df.iloc[r_idx, c_idx]
                try:
                    f = float(val)
                except Exception:
                    continue

                bg = None
                if f <= PCT_DROP_THRESHOLD_STRONG:
                    bg = "#03ff18"
                elif f <= PCT_DROP_THRESHOLD_SOFT:
                    bg = "#eaffea"
                elif f >= PCT_RISE_THRESHOLD_STRONG:
                    bg = "#fbff17"   # strong green
                elif f >= PCT_RISE_THRESHOLD_SOFT:
                    bg = "#fcffcd"   # soft yellow
                else:
                    continue

                # tksheet API: highlight_cells(row=..., column=..., bg=..., redraw=...)
                try:
                    self.widget.highlight_cells(row=r_idx, column=c_idx, bg=bg, redraw=False)
                except TypeError:
                    # Older tksheet versions may use keyword 'color' instead of 'bg'
                    self.widget.highlight_cells(row=r_idx, column=c_idx, color=bg, redraw=False)
                except Exception:
                    pass

        # One repaint at the end for speed
        try:
            self.widget.redraw()
        except Exception:
            self.widget.refresh()


# -------------------- Main App --------------------

class StockDropsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stock Drops (3/4/5-day) – Tk GUI")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.tickers = list(DEFAULT_TICKERS)
        self.data = {}

        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Tickers (comma-separated, AAPL,MSFT,...):").pack(side=tk.LEFT)
        self.entry = ttk.Entry(top, width=70)
        self.entry.pack(side=tk.LEFT, padx=8)
        self.entry.insert(0, ",".join(self.tickers))

        self.btn_add     = ttk.Button(top, text="Add",          command=self.on_add)
        self.btn_replace = ttk.Button(top, text="Replace",      command=self.on_replace)
        self.btn_refresh = ttk.Button(top, text="Refresh",      command=self.on_refresh)
        self.btn_export  = ttk.Button(top, text="Export Excel", command=self.on_export)
        for b in (self.btn_add, self.btn_replace, self.btn_refresh, self.btn_export):
            b.pack(side=tk.LEFT, padx=4)

        self.status = ttk.Label(self, text=("Ready. "
                          + ("(tksheet enabled: per-cell colors)"
                             if HAS_TKSHEET else "(fallback: row-level colors)")), anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.nb = ttk.Notebook(self)
        self.nb.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)

        self.tables = {}   # {horizon: {"full": Table, "last": Table}}
        for n, label in HORIZONS:
            frame = ttk.Frame(self.nb)
            self.nb.add(frame, text=label)

            paned = ttk.PanedWindow(frame, orient=tk.VERTICAL)
            paned.pack(expand=True, fill=tk.BOTH)

            full_frame = ttk.LabelFrame(paned, text=f"{label} – All rows (≤ {abs(PCT_DROP_THRESHOLD_SOFT)}%)")
            table_full = Table(full_frame)
            paned.add(full_frame, weight=3)

            last_frame = ttk.LabelFrame(paned, text=f"{label} – Latest day only")
            table_last = Table(last_frame)
            paned.add(last_frame, weight=1)

            self.tables[n] = {"full": table_full, "last": table_last}

        self.after(100, self.on_refresh)

    # --------------- UI Utilities ---------------

    def _parse_tickers(self, text):
        raw = [t.strip().upper() for t in text.split(",") if t.strip()]
        return [t for t in raw if re.match(r"^[A-Z0-9]+$", t)]

    def _lock_ui(self, locked=True, msg=""):
        for b in (self.btn_add, self.btn_replace, self.btn_refresh, self.btn_export):
            b.configure(state=tk.DISABLED if locked else tk.NORMAL)
        self.entry.configure(state=tk.DISABLED if locked else tk.NORMAL)
        if msg:
            self.status.configure(text=msg)

    def _apply_data_to_ui(self):
        for n, _label in HORIZONS:
            full, last = self.data.get(n, (pd.DataFrame(), pd.DataFrame()))
            self.tables[n]["full"].set_dataframe(full)
            self.tables[n]["last"].set_dataframe(last)
            # Per-cell color (tksheet only)
            self.tables[n]["full"].colorize_cells(full)
            self.tables[n]["last"].colorize_cells(last)

    # --------------- Button handlers ---------------

    def on_add(self):
        new = self._parse_tickers(self.entry.get())
        if not new:
            messagebox.showwarning("No valid tickers", "Enter comma-separated tickers like AAPL,MSFT")
            return
        before = set(self.tickers)
        for t in new:
            if t not in before:
                self.tickers.append(t)
        self.status.configure(text=f"Added {len(set(new)-before)} new tickers. Total: {len(self.tickers)}")

    def on_replace(self):
        new = self._parse_tickers(self.entry.get())
        if not new:
            messagebox.showwarning("No valid tickers", "Enter comma-separated tickers like AAPL,MSFT")
            return
        self.tickers = new
        self.status.configure(text=f"Replaced ticker list. Total: {len(self.tickers)}")

    def on_refresh(self):
        self._lock_ui(True, "Fetching data…")
        threading.Thread(target=self._do_refresh, daemon=True).start()

    def _do_refresh(self):
        try:
            five, four, three = fetch_stock_data(self.tickers)
            self.data = {
                5: (five, df_latest_row(five)),
                4: (four, df_latest_row(four)),
                3: (three, df_latest_row(three)),
            }
            self.after(0, self._apply_data_to_ui)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self._lock_ui(False, "Ready."))

    def on_export(self):
        if not self.data:
            messagebox.showinfo("Nothing to export", "Fetch data first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")]
        )
        if not path:
            return
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                row = 1
                for n, label in HORIZONS:
                    full, last = self.data.get(n, (pd.DataFrame(), pd.DataFrame()))
                    pd.DataFrame(columns=[f"{label} Drops (≤{abs(PCT_DROP_THRESHOLD_SOFT)}%)"]).to_excel(
                        writer, sheet_name="Sheet1", index=False, startrow=row
                    )
                    full.to_excel(writer, sheet_name="Sheet1", index=False, startrow=row+1)
                    row += max(2, len(full) + 4)
                    pd.DataFrame(columns=[f"{label} Latest"]).to_excel(
                        writer, sheet_name="Sheet1", index=False, startrow=row
                    )
                    last.to_excel(writer, sheet_name="Sheet1", index=False, startrow=row+1)
                    row += max(2, len(last) + 4)
            self.status.configure(text=f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

if __name__ == "__main__":
    app = StockDropsApp()
    app.mainloop()
