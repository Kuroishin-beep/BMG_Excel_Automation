import streamlit as st
import pandas as pd
from io import BytesIO
import re

# =============================================================================================
# CONFIGURATION & UTILS
# =============================================================================================
try:
    from utils import load_logo
    from config import AppConfig
except ImportError:
    class AppConfig:
        APP_TITLE = "Book Segregation Tool"
    def load_logo(): return None


# =============================================================================================
# CLASSIFIER
# =============================================================================================

class BookCategoryClassifier:

    def _get_column_name(self, df: pd.DataFrame, candidates: list) -> str:
        cols = {c.lower().strip(): c for c in df.columns}
        for cand in candidates:
            if cand.lower() in cols:
                return cols[cand.lower()]
        return None

    def clean_reversals(self, df: pd.DataFrame) -> pd.DataFrame:
        target_cols = [
            self._get_column_name(df, ["narration"]),
            self._get_column_name(df, ["description"])
        ]
        target_cols = [c for c in target_cols if c]

        if not target_cols:
            return df

        pattern = r"(reversal of|reversed)"
        mask = pd.Series(False, index=df.index)

        for col in target_cols:
            mask |= df[col].astype(str).str.contains(pattern, case=False, regex=True, na=False)

        return df[~mask].copy()

    def segregate(self, df: pd.DataFrame) -> dict:

        df = self.clean_reversals(df.copy())

        # Identify columns
        id_col = self._get_column_name(df, ["journal id", "journal no", "id", "transaction id"])
        account_col = self._get_column_name(df, ["account", "account title", "account code"])
        debit_col = self._get_column_name(df, ["debit", "dr"])
        credit_col = self._get_column_name(df, ["credit", "cr"])
        narration_col = self._get_column_name(df, ["narration", "description", "memo"])
        date_col = self._get_column_name(df, ["date"])

        if not all([id_col, account_col, debit_col, credit_col]):
            raise ValueError("Missing required columns")

        # Clean and forward-fill Journal IDs
        df[id_col] = df[id_col].astype(str).str.strip()
        df[id_col] = df[id_col].replace(
            to_replace=r"^(total|grand total|nan|none|\s*)$",
            value=pd.NA,
            regex=True
        )
        df[id_col] = df[id_col].ffill()
        df = df.dropna(subset=[id_col])

        # Ensure numeric
        df[debit_col] = pd.to_numeric(df[debit_col], errors="coerce").fillna(0)
        df[credit_col] = pd.to_numeric(df[credit_col], errors="coerce").fillna(0)

        # Text normalization
        acc_text = df[account_col].astype(str).str.lower()
        narr_text = (
            df[narration_col].astype(str).str.lower()
            if narration_col else pd.Series("", index=df.index)
        )

        # Account identification
        is_bank = acc_text.str.contains(r"rcbc|westpac", na=False) | \
                  narr_text.str.contains(r"rcbc|westpac", na=False)

        is_ap = acc_text.str.contains(r"accounts payable|trade creditors", na=False)
        is_ar = acc_text.str.contains(r"trade debtors|accounts receivable", na=False)

        # Triggers
        df["__is_receipt"] = (is_bank & (df[debit_col] > 0)) | (is_ar & (df[credit_col] > 0))
        df["__is_disburse"] = (is_bank & (df[credit_col] > 0)) | (is_ap & (df[debit_col] > 0))

        # Group logic
        grp_receipt = df.groupby(id_col)["__is_receipt"].transform("any")
        grp_disburse = df.groupby(id_col)["__is_disburse"].transform("any")

        # Manual row flag (Date ends with "- Manual")
        df["__is_manual"] = False
        if date_col:
            df["__is_manual"] = df[date_col].astype(str).str.contains(
                r"-\s*manual\s*$", case=False, regex=True, na=False
            )

        # Final assignment
        def assign_book(idx):
            if df.loc[idx, "__is_manual"]:
                return "General Journal"
            if grp_receipt[idx]:
                return "Cash Receipts"
            if grp_disburse[idx]:
                return "Cash Disbursement"
            return "General Journal"

        df["Book"] = df.index.to_series().apply(assign_book)

        df = df.drop(columns=["__is_receipt", "__is_disburse", "__is_manual"])

        return {
            "Cash Disbursement": df[df["Book"] == "Cash Disbursement"].drop(columns="Book"),
            "Cash Receipts": df[df["Book"] == "Cash Receipts"].drop(columns="Book"),
            "General Journal": df[df["Book"] == "General Journal"].drop(columns="Book"),
        }


# =============================================================================================
# UI
# =============================================================================================

def render_segregation_page():

    logo_url = load_logo()
    if logo_url:
        st.markdown(
            f"<div class='nav-bar'><img src='{logo_url}' height='40'><h2>{AppConfig.APP_TITLE}</h2></div>",
            unsafe_allow_html=True,
        )

    st.subheader("Automatic Book Segregation")

    if st.session_state.get("processed_df") is not None:
        df = st.session_state.processed_df
    elif st.session_state.get("df_original") is not None:
        df = st.session_state.df_original
    else:
        st.error("No data available.")
        st.stop()

    classifier = BookCategoryClassifier()
    segregated = classifier.segregate(df)

    for name, sdf in segregated.items():
        st.markdown(f"### {name} ({len(sdf)} rows)")
        st.dataframe(sdf, use_container_width=True)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for name, sdf in segregated.items():
            sdf.to_excel(writer, sheet_name=name, index=False)

    original = st.session_state.get("original_filename", "Excel_File.xlsx")
    base = re.sub(r"\.xlsx?$", "", original, flags=re.IGNORECASE)
    output_name = f"{base}_Segregated.xlsx"

    st.download_button(
        "Download Excel File",
        buffer.getvalue(),
        file_name=output_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
