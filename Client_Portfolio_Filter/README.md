# Client Portfolio Filter

An interactive filtering and visualization tool for client portfolio holdings.  
This application loads client data from CSVs, applies configurable filters on asset allocation, and displays results in a browser-style desktop app with interactive charts.

![Screenshot](<./Example Application Query Output.png>)

> Above is an example of the application query output.

> **Note**: Numerical values have been redacted due to data sensitivity.
---

## Features
- **Flexible filters**:
  - Filter portfolios by one or two **asset classes** (e.g., Cash, Common Stock).  
  - Add an optional **sector filter** for Common Stock.  
  - Support for `<`, `>`, or `≈` (±3%) thresholds.  
- **Dynamic charts**:
  - Portfolio **asset class breakdown** (pie chart).  
  - Portfolio **common stock by sector** (pie chart).  
- **Tabular results**:
  - Portfolio → Short Name → Accounts (cash rows).  
  - Percent allocation for each filter.  
  - Portfolio value and cash holdings.  
- **Sorting tools**:
  - Order results by Class #1, Class #2, Sector, or Cash.  
- **Export**:
  - Download filtered results as a formatted Excel file (percentages, cash, portfolio values).

---

## Input Data

Two CSV files must be placed in the same directory as the executable/script:

1. **`Client_Data.csv`** – main portfolio holdings file.  
   Expected columns (exact names flexible; tolerant matching is used):
   - Portfolio Name  
   - Account Number  
   - Short Name (if missing, filled via mapping)  
   - Asset Class (e.g., Common Stock, Cash and Equivalents)  
   - Segment (sector, for stocks)  
   - Market Value  

   Example:

   ![Screenshot](<./Client Data Format Example.png>)

2. **`ShortName_Map.csv`** – mapping of account numbers to short names.  
   - Columns: `Account Number`, `Short Name`.

---

## How to Run

### Python
```bash
pip install -r requirements.txt
python app.py
```









