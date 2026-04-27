"""
╔══════════════════════════════════════════════════════════════╗
║           Lucy Gurlsnte Mess Bill - Streamlit App            ║
║                                                              ║
║  README / ERROR HANDLING GUIDE:                              ║
║  ─────────────────────────────                               ║
║  Q: What if more "Full" plates are entered than Total Count? ║
║  A: The app validates in real time. If the number of people  ║
║     who selected "Full" exceeds the Total Food Count, it     ║
║     will display a red warning and BLOCK submission until    ║
║     corrected. For example:                                  ║
║       - Total Lunch Count = 2                                ║
║       - 3 people marked "Full"                               ║
║       → Error: "Full eaters (3) exceed Total Count (2)!"    ║
║     Simply reduce the Total Count or change some statuses   ║
║     from "Full" to "Shared" or "None" to resolve this.      ║
║                                                              ║
║  The "Shared Pool" can never be negative. If fulls == total, ║
║  shared pool = 0, and "Shared" people pay ₹0 for that meal. ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import os
from datetime import date, datetime
import calendar

# ── Constants ─────────────────────────────────────────────────
RESIDENTS = ["Nair", "Lachu", "Anannya", "Aneena", "Devananda",
             "Gayathri", "Gopika", "Ravi", "Sai", "Rajesh", "Upasana", "Others"]

MEAL_RATES = {"Bf": 40, "Lunch": 50, "Dinner": 60}
CSV_FILE = "mess_data.csv"
HISTORY_FILE = "mess_history.csv"

COLUMNS = ["date", "meal", "total_count"] + \
          [f"{r}_status" for r in RESIDENTS] + \
          [f"{r}_cost" for r in RESIDENTS]

HISTORY_COLUMNS = ["month", "closed_on"] + \
                  [f"{r}_total" for r in RESIDENTS]

# ── Baby Pink Custom CSS ───────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');

/* Global background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #FFD1DC !important;
    font-family: 'Nunito', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #ffb8cc !important;
    border-right: 3px solid #ff8fab;
}

[data-testid="stSidebar"] * {
    color: #5c2d3e !important;
}

/* Title styling */
.main-title {
    font-family: 'Fredoka One', cursive;
    font-size: 2.8rem;
    color: #c0365a;
    text-align: center;
    text-shadow: 3px 3px 0px #ffafcc, 5px 5px 0px #ff8fab33;
    letter-spacing: 1px;
    margin-bottom: 0.2rem;
}

.subtitle {
    text-align: center;
    color: #e0607e;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Cards */
.pink-card {
    background: rgba(255,255,255,0.6);
    border: 2px solid #ffafcc;
    border-radius: 20px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(192,54,90,0.1);
}

.meal-header {
    font-family: 'Fredoka One', cursive;
    font-size: 1.4rem;
    color: #c0365a;
    margin-bottom: 0.5rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff8fab, #c0365a) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    padding: 0.5rem 2rem !important;
    box-shadow: 0 4px 12px rgba(192,54,90,0.35) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(192,54,90,0.5) !important;
}

/* Selectbox and inputs - force visible text */
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 2px solid #ffafcc !important;
    background: #ffffff !important;
    color: #5c2d3e !important;
}

/* The selected value text inside selectbox */
.stSelectbox > div > div > div {
    color: #5c2d3e !important;
    font-weight: 700 !important;
    background: #ffffff !important;
}

/* Selectbox SVG arrow icon */
.stSelectbox svg {
    fill: #c0365a !important;
}

/* Dropdown list popup */
[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 2px solid #ffafcc !important;
    border-radius: 12px !important;
    color: #5c2d3e !important;
}

/* Dropdown option items */
[data-baseweb="menu"] li, [role="option"] {
    background: #ffffff !important;
    color: #5c2d3e !important;
    font-weight: 600 !important;
}

[data-baseweb="menu"] li:hover, [role="option"]:hover {
    background: #ffe0ea !important;
    color: #c0365a !important;
}

/* Number input */
.stNumberInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #ffafcc !important;
    background: #ffffff !important;
    color: #5c2d3e !important;
    font-weight: 700 !important;
}

/* Date input */
.stDateInput > div > div > input {
    background: #ffffff !important;
    color: #5c2d3e !important;
    border: 2px solid #ffafcc !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

/* Tables */
.stDataFrame {
    border-radius: 16px !important;
    overflow: hidden;
}

thead tr th {
    background-color: #ff8fab !important;
    color: white !important;
    font-family: 'Fredoka One', cursive !important;
}

/* Alert boxes */
.stAlert {
    border-radius: 14px !important;
}

/* Divider */
hr {
    border-color: #ffafcc;
    margin: 1rem 0;
}

/* Metric */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.5);
    border: 1.5px solid #ffafcc;
    border-radius: 14px;
    padding: 0.5rem 1rem;
}

[data-testid="stMetricLabel"] {
    color: #c0365a !important;
    font-weight: 800 !important;
}

[data-testid="stMetricValue"] {
    color: #5c2d3e !important;
    font-family: 'Fredoka One', cursive !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.4);
    border-radius: 50px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 50px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #c0365a !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff8fab, #c0365a) !important;
    color: white !important;
}

/* Section labels */
label, .stRadio label {
    font-weight: 700 !important;
    color: #5c2d3e !important;
}
</style>
"""

# ── Data Helpers ───────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # ensure all columns exist
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = 0 if "_cost" in col else ("None" if "_status" in col else "")
        return df
    else:
        return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False)


def load_history() -> pd.DataFrame:
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame(columns=HISTORY_COLUMNS)


def save_history(df: pd.DataFrame):
    df.to_csv(HISTORY_FILE, index=False)


# ── Calculation Engine ─────────────────────────────────────────
def compute_meal_costs(total_count: int, statuses: dict, meal: str) -> dict:
    """
    Returns per-person cost for a meal.
    statuses: {resident: "Full" | "Shared" | "None"}
    """
    rate = MEAL_RATES[meal]
    full_people = [r for r, s in statuses.items() if s == "Full"]
    shared_people = [r for r, s in statuses.items() if s == "Shared"]

    n_full = len(full_people)

    # Validation
    if n_full > total_count:
        return None  # caller handles error

    remaining = total_count - n_full
    shared_pool_cost = remaining * rate

    shared_per_person = 0.0
    if shared_people and remaining > 0:
        shared_per_person = shared_pool_cost / len(shared_people)

    costs = {}
    for r in RESIDENTS:
        status = statuses.get(r, "None")
        if status == "Full":
            costs[r] = float(rate)
        elif status == "Shared":
            costs[r] = round(shared_per_person, 2)
        else:
            costs[r] = 0.0
    return costs


def get_month_totals(df: pd.DataFrame, year: int, month: int) -> pd.Series:
    if df.empty:
        return pd.Series({r: 0.0 for r in RESIDENTS})
    month_str = f"{year}-{month:02d}"
    mask = df["date"].astype(str).str.startswith(month_str)
    filtered = df[mask]
    if filtered.empty:
        return pd.Series({r: 0.0 for r in RESIDENTS})
    totals = {}
    for r in RESIDENTS:
        col = f"{r}_cost"
        totals[r] = filtered[col].sum() if col in filtered.columns else 0.0
    return pd.Series(totals)


# ── Streamlit App ──────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Lucy Gurlsnte Mess Bill 🌸",
        page_icon="🌸",
        layout="wide",
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Title
    st.markdown('<div class="main-title">🌸 Lucy Gurlsnte Mess Bill 🌸</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">✨ Track • Split • Settle ✨</div>', unsafe_allow_html=True)

    # Load data
    df = load_data()

    # Sidebar – Month Dashboard
    with st.sidebar:
        st.markdown("### 📅 Month Dashboard")
        today = date.today()
        sel_year = st.selectbox("Year", list(range(2024, today.year + 2)), index=list(range(2024, today.year + 2)).index(today.year))
        sel_month = st.selectbox("Month", list(range(1, 13)), index=today.month - 1,
                                  format_func=lambda m: calendar.month_name[m])

        totals = get_month_totals(df, sel_year, sel_month)
        st.markdown("---")
        st.markdown("**💰 Current Totals**")
        for r in RESIDENTS:
            st.metric(label=r, value=f"₹{totals[r]:.2f}")

        st.markdown("---")
        grand = totals.sum()
        st.metric(label="🧾 Grand Total", value=f"₹{grand:.2f}")

    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Daily Entry", "📊 View Records", "📁 Close Month", "📜 History"])

    # ── TAB 1: Daily Entry ─────────────────────────────────────
    with tab1:
        st.markdown('<div class="pink-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Add Daily Meal Entry")
        entry_date = st.date_input("Select Date", value=today, max_value=today)
        st.markdown('</div>', unsafe_allow_html=True)

        meal_data = {}

        for meal, rate in MEAL_RATES.items():
            emoji = {"Bf": "🌅", "Lunch": "☀️", "Dinner": "🌙"}[meal]
            st.markdown(f'<div class="pink-card"><div class="meal-header">{emoji} {meal} — ₹{rate}/plate</div>', unsafe_allow_html=True)

            total_count = st.number_input(
                f"Total {meal} Count (plates ordered)",
                min_value=0, max_value=50, value=0,
                key=f"total_{meal}"
            )

            statuses = {}
            if total_count > 0:
                cols = st.columns(4)
                for i, resident in enumerate(RESIDENTS):
                    with cols[i % 4]:
                        status = st.selectbox(
                            resident,
                            ["None", "Full", "Shared"],
                            key=f"{meal}_{resident}_status"
                        )
                        statuses[resident] = status
            else:
                for r in RESIDENTS:
                    statuses[r] = "None"

            # Live validation
            n_full = sum(1 for s in statuses.values() if s == "Full")
            if total_count > 0 and n_full > total_count:
                st.error(f"🚨 Full eaters ({n_full}) exceed Total Count ({total_count})! Please fix before saving.")
                meal_data[meal] = {"valid": False, "total": total_count, "statuses": statuses}
            else:
                if total_count > 0:
                    costs = compute_meal_costs(total_count, statuses, meal)
                    if costs:
                        preview_df = pd.DataFrame({
                            "Person": list(costs.keys()),
                            "Status": [statuses[r] for r in costs.keys()],
                            "Cost (₹)": [f"₹{v:.2f}" for v in costs.values()]
                        })
                        preview_df = preview_df[preview_df["Status"] != "None"]
                        if not preview_df.empty:
                            st.markdown("**Preview:**")
                            st.dataframe(preview_df, hide_index=True, use_container_width=True)
                meal_data[meal] = {"valid": True, "total": total_count, "statuses": statuses}

            st.markdown('</div>', unsafe_allow_html=True)

        # Save button
        all_valid = all(v["valid"] for v in meal_data.values())
        has_data = any(v["total"] > 0 for v in meal_data.values())

        if st.button("💾 Save Today's Entry", disabled=not (all_valid and has_data)):
            rows_to_add = []
            for meal in MEAL_RATES:
                md = meal_data[meal]
                if md["total"] == 0:
                    continue
                costs = compute_meal_costs(md["total"], md["statuses"], meal)
                row = {
                    "date": entry_date.strftime("%Y-%m-%d"),
                    "meal": meal,
                    "total_count": md["total"]
                }
                for r in RESIDENTS:
                    row[f"{r}_status"] = md["statuses"].get(r, "None")
                    row[f"{r}_cost"] = costs.get(r, 0.0)
                rows_to_add.append(row)

            if rows_to_add:
                new_rows = pd.DataFrame(rows_to_add)
                df = pd.concat([df, new_rows], ignore_index=True)
                save_data(df)
                st.success("✅ Entry saved successfully! 🌸")
                st.balloons()

    # ── TAB 2: View Records ────────────────────────────────────
    with tab2:
        st.markdown("### 📊 Records for Selected Month")
        if df.empty:
            st.info("No records yet. Add entries from the Daily Entry tab!")
        else:
            month_str = f"{sel_year}-{sel_month:02d}"
            mask = df["date"].astype(str).str.startswith(month_str)
            month_df = df[mask].copy()

            if month_df.empty:
                st.info(f"No records for {calendar.month_name[sel_month]} {sel_year}.")
            else:
                st.markdown(f"**{len(month_df)} records found**")

                # Show summary table
                totals = get_month_totals(df, sel_year, sel_month)
                summary_df = pd.DataFrame({
                    "Resident": totals.index,
                    "Total Owed (₹)": totals.values.round(2)
                }).sort_values("Total Owed (₹)", ascending=False)

                st.dataframe(summary_df, hide_index=True, use_container_width=True)

                st.markdown("---")
                with st.expander("🔍 View Raw Daily Records"):
                    display_cols = ["date", "meal", "total_count"] + [f"{r}_cost" for r in RESIDENTS]
                    st.dataframe(month_df[display_cols].rename(
                        columns={f"{r}_cost": r for r in RESIDENTS}
                    ), hide_index=True, use_container_width=True)

                # Delete a record
                st.markdown("---")
                st.markdown("**🗑️ Delete a Record**")
                if not month_df.empty:
                    row_options = [f"{row['date']} | {row['meal']}" for _, row in month_df.iterrows()]
                    del_choice = st.selectbox("Select record to delete", ["-- Select --"] + row_options)
                    if del_choice != "-- Select --" and st.button("Delete Selected Record"):
                        idx = row_options.index(del_choice)
                        actual_idx = month_df.index[idx]
                        df = df.drop(index=actual_idx).reset_index(drop=True)
                        save_data(df)
                        st.success("Record deleted!")
                        st.rerun()

    # ── TAB 3: Close Month ─────────────────────────────────────
    with tab3:
        st.markdown("### 📁 Close & Archive Month")
        st.warning("⚠️ Closing a month will save final totals to history and remove those records from the active file.")

        month_str = f"{sel_year}-{sel_month:02d}"
        mask = df["date"].astype(str).str.startswith(month_str)
        month_records = df[mask]

        if month_records.empty:
            st.info(f"No records for {calendar.month_name[sel_month]} {sel_year} to close.")
        else:
            totals = get_month_totals(df, sel_year, sel_month)
            st.markdown(f"**Final Bill for {calendar.month_name[sel_month]} {sel_year}:**")
            final_df = pd.DataFrame({
                "Resident": totals.index,
                "Amount Due (₹)": [f"₹{v:.2f}" for v in totals.values]
            })
            st.dataframe(final_df, hide_index=True, use_container_width=True)
            st.metric("Total Collection", f"₹{totals.sum():.2f}")

            confirm = st.checkbox("✅ I confirm I want to close this month")
            if confirm and st.button("🔒 Close Month & Archive"):
                history = load_history()
                new_hist_row = {"month": month_str, "closed_on": datetime.now().strftime("%Y-%m-%d %H:%M")}
                for r in RESIDENTS:
                    new_hist_row[f"{r}_total"] = round(totals[r], 2)
                history = pd.concat([history, pd.DataFrame([new_hist_row])], ignore_index=True)
                save_history(history)

                # Remove closed month from active data
                df = df[~mask].reset_index(drop=True)
                save_data(df)
                st.success(f"✅ {calendar.month_name[sel_month]} {sel_year} has been closed and archived! 🎉")
                st.balloons()
                st.rerun()

    # ── TAB 4: History ─────────────────────────────────────────
    with tab4:
        st.markdown("### 📜 Archived Monthly Bills")
        history = load_history()
        if history.empty:
            st.info("No archived months yet. Close a month to see it here!")
        else:
            for _, row in history.iterrows():
                month_label = row.get("month", "Unknown")
                closed = row.get("closed_on", "")
                with st.expander(f"📅 {month_label}  (closed: {closed})"):
                    hist_data = {r: row.get(f"{r}_total", 0) for r in RESIDENTS}
                    hist_df = pd.DataFrame({
                        "Resident": list(hist_data.keys()),
                        "Amount Paid (₹)": [f"₹{v:.2f}" for v in hist_data.values()]
                    })
                    st.dataframe(hist_df, hide_index=True, use_container_width=True)
                    total_collected = sum(hist_data.values())
                    st.metric("Total Collected", f"₹{total_collected:.2f}")


if __name__ == "__main__":
    main()