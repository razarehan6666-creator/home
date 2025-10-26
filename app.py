from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# Replace with your published Google Sheets CSV link
EXCEL_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPIR5j2TyzJAorJsGX9reIhOXQKrTfyDbbv2GreXPDf2nWcBCddhoedW93yEaK1S93imugCke-dRD_/pub?output=csv"

# Columns we expect (all uppercase normalization will be applied)
EXPECTED_COLUMNS = [
    "MONTH",
    "PAID",
    "NO. OF DAYS IN MONTH",
    "NO. OF DAYS ABSENT",
    "NO. OF DAYS COMING",
    "AMOUNT",
    "PAYMENT MODE"   # new column added
]

def get_month_data(month_name):
    """
    Fetch CSV from Google Sheets, normalize headers, find row for month_name,
    and return a dictionary including PAYMENT MODE.
    """
    try:
        df = pd.read_csv(EXCEL_URL)
    except Exception as e:
        return {"error": f"Cannot fetch Google Sheet: {e}"}

    # Normalize column names: strip whitespace and uppercase them
    df.columns = df.columns.str.strip().str.upper()

    # Ensure dataframe has expected columns (not required, but helpful to warn)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        # Not fatal: we will still try to return available fields, but inform user
        # Note: In production you might want to log this instead.
        return {"error": f"Google Sheet missing expected columns: {', '.join(missing)}"}

    # Filter rows for the requested month (case-insensitive, trimmed)
    # Some rows might have NaN in MONTH - skip them safely
    mask = df['MONTH'].astype(str).str.strip().str.upper() == month_name.strip().upper()
    month_rows = df[mask]

    if month_rows.empty:
        return {"error": "No data found for this month"}

    row = month_rows.iloc[0]

    # Use Series.get to provide sensible defaults if some cell is empty
    return {
        "Month": row.get("MONTH", ""),
        "Paid": row.get("PAID", ""),
        "Days in Month": row.get("NO. OF DAYS IN MONTH", ""),
        "Days Absent": row.get("NO. OF DAYS ABSENT", ""),
        "Days Coming": row.get("NO. OF DAYS COMING", ""),
        "Amount": row.get("AMOUNT", ""),
        "Payment Mode": row.get("PAYMENT MODE", "")   # new field returned
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/month/<month_name>")
def month_data(month_name):
    return jsonify(get_month_data(month_name))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)








