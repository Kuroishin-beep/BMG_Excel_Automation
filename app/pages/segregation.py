"""
Book Segregation module for the Excel Duplicate Delete application.

This module automatically classifies accounting transactions into three books:
- Cash Disbursement (expenses, payments)
- Cash Receipts (income, collections)
- General Journal (other transactions)
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import re
from pathlib import Path
import sys

# Add the parent directory to sys.path to import from utils and constants
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils import load_logo
    from constants import CSS_STYLES, UI_LABELS, COLOR_CODES
    from config import AppConfig
except ImportError:
    class AppConfig:
        APP_TITLE = "Book Segregation Tool"
    def load_logo(): return None


# =============================================================================================
# CLASSIFIER (UPDATED: CALCULATES TOTALS ON TOTAL ROW)
# =============================================================================================

class BookCategoryClassifier:
    """
    Classifier that segregates accounting data into Cash Disbursement, 
    Cash Receipts, and General Journal books based on account patterns.
    """

    def _get_column_name(self, df: pd.DataFrame, candidates: list) -> str:
        """Find column name from list of candidates (case-insensitive)."""
        cols = {c.lower().strip(): c for c in df.columns}
        for cand in candidates:
            if cand.lower() in cols:
                return cols[cand.lower()]
        return None

    def clean_reversals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove reversal entries from the dataframe."""
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
        """
        Segregate dataframe into three books based on account patterns.
        - Fixes ID mismatches (Description ID > Column ID).
        - Sorts groups by date (Header > Body > Footer).
        - CALCULATES TOTALS: Sums Debit/Credit and puts them on the 'Total' row.
        - Inserts 1 blank row between groups.
        """
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

        # -------------------------------------------------------------------------
        # 1. FIX ID MISMATCH (Description ID > Column ID)
        # -------------------------------------------------------------------------
        if date_col:
            extracted_ids = df[date_col].astype(str).str.extract(r'(?i)ID\s+(\d+)', expand=False)
            extracted_ids = extracted_ids.ffill()
            if not extracted_ids.isna().all():
                df[id_col] = extracted_ids.combine_first(df[id_col])

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

        # -------------------------------------------------------------------------
        # 2. CLEAN "GHOST" ROWS
        # -------------------------------------------------------------------------
        def is_blank(series):
            return series.isna() | series.astype(str).str.strip().str.lower().isin(['', 'nan', 'none'])

        mask_date_blank = is_blank(df[date_col])
        mask_acct_blank = is_blank(df[account_col])
        mask_zero_money = (df[debit_col] == 0) & (df[credit_col] == 0)

        mask_junk = mask_date_blank & mask_acct_blank & mask_zero_money
        df = df[~mask_junk].copy()

        # Text normalization & Classification Logic
        acc_text = df[account_col].astype(str).str.lower()
        narr_text = (
            df[narration_col].astype(str).str.lower()
            if narration_col else pd.Series("", index=df.index)
        )

        is_bank = acc_text.str.contains(r"rcbc|westpac", na=False) | \
                  narr_text.str.contains(r"rcbc|westpac", na=False)
        is_ap = acc_text.str.contains(r"accounts payable|trade creditors", na=False)
        is_ar = acc_text.str.contains(r"trade debtors|accounts receivable", na=False)

        df["__is_receipt"] = (is_bank & (df[debit_col] > 0)) | (is_ar & (df[credit_col] > 0))
        df["__is_disburse"] = (is_bank & (df[credit_col] > 0)) | (is_ap & (df[debit_col] > 0))

        grp_receipt = df.groupby(id_col)["__is_receipt"].transform("any")
        grp_disburse = df.groupby(id_col)["__is_disburse"].transform("any")

        df["__is_manual"] = False
        if date_col:
            df["__is_manual"] = df[date_col].astype(str).str.contains(
                r"-\s*manual\s*$", case=False, regex=True, na=False
            )

        def assign_book(idx):
            if df.loc[idx, "__is_manual"]: return "General Journal"
            if grp_receipt[idx]: return "Cash Receipts"
            if grp_disburse[idx]: return "Cash Disbursement"
            return "General Journal"

        df["Book"] = df.index.to_series().apply(assign_book)
        df = df.drop(columns=["__is_receipt", "__is_disburse", "__is_manual"])

        # Create results dictionary
        results = {
            "Cash Disbursement": df[df["Book"] == "Cash Disbursement"].drop(columns="Book"),
            "Cash Receipts": df[df["Book"] == "Cash Receipts"].drop(columns="Book"),
            "General Journal": df[df["Book"] == "General Journal"].drop(columns="Book"),
        }

        # -------------------------------------------------------------------------
        # 3. SORTING, TOTAL CALCULATION & SPACER INSERTION
        # -------------------------------------------------------------------------
        if date_col:
            for key, book_df in results.items():
                if book_df.empty:
                    continue
                
                try:
                    book_df = book_df.copy()
                    
                    # Sort Logic
                    book_df['__temp_sort_date'] = pd.to_datetime(book_df[date_col], errors='coerce')
                    book_df['__group_sort_date'] = book_df.groupby(id_col)['__temp_sort_date'].transform('min')
                    
                    is_footer = book_df[date_col].astype(str).str.contains(r'^(Total|None|Grand Total)', case=False, na=False)
                    is_valid_date = book_df['__temp_sort_date'].notna()
                    
                    book_df['__row_rank'] = 0
                    book_df.loc[is_valid_date, '__row_rank'] = 1
                    book_df.loc[is_footer, '__row_rank'] = 2

                    book_df = book_df.sort_values(
                        by=['__group_sort_date', id_col, '__row_rank'], 
                        ascending=[True, True, True],
                        na_position='last'
                    )
                    
                    # Process Groups: Insert Spacer & Calculate Totals
                    sorted_groups = []
                    unique_ids = book_df[id_col].unique()
                    
                    blank_row = pd.DataFrame([pd.NA] * len(book_df.columns), index=book_df.columns).T
                    blank_row = blank_row.drop(columns=['__temp_sort_date', '__group_sort_date', '__row_rank'], errors='ignore')

                    for j_id in unique_ids:
                        group = book_df[book_df[id_col] == j_id].copy()
                        group = group.drop(columns=['__temp_sort_date', '__group_sort_date', '__row_rank'])
                        
                        # --- CALCULATION LOGIC STARTS HERE ---
                        # Find the Total row
                        total_mask = group[date_col].astype(str).str.contains(r'^(Total|Grand Total)', case=False, na=False)
                        
                        if total_mask.any():
                            # Sum only the Non-Total rows
                            debit_sum = group.loc[~total_mask, debit_col].sum()
                            credit_sum = group.loc[~total_mask, credit_col].sum()
                            
                            # Assign sums to the Total row
                            group.loc[total_mask, debit_col] = debit_sum
                            group.loc[total_mask, credit_col] = credit_sum
                        # --- CALCULATION LOGIC ENDS HERE ---

                        sorted_groups.append(group)
                        sorted_groups.append(blank_row)
                    
                    if sorted_groups:
                        final_df = pd.concat(sorted_groups[:-1], ignore_index=True)
                        results[key] = final_df
                    else:
                        results[key] = book_df.drop(columns=['__temp_sort_date', '__group_sort_date', '__row_rank'])
                    
                except Exception:
                    pass

        return results


def go_back_to_workspace():
    """Navigate back to workspace page."""
    st.session_state.current_page = 'workspace'
    st.rerun()


# =============================================================================================
# UI RENDERING
# =============================================================================================

def render_segregation_page():
    """
    Render the book segregation page with clean colorful design.
    """
    
    # Custom CSS matching workspace color palette
    st.markdown("""
        <style>
        .nav-bar {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .nav-title {
            color: white !important;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }
        .nav-subtitle {
            color: white !important;
            font-size: 1rem;
            margin: 0.25rem 0 0 0;
        }
        .logo-container {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .logo-image {
            height: 50px;
            width: auto;
        }
        .section-header-orange {
            background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.3);
        }
        .section-header-blue {
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.3);
        }
        .section-header-green {
            background: linear-gradient(135deg, #16a34a 0%, #4ade80 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.3);
        }
        .rule-card-orange {
            background: #fff7ed;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.75rem 0;
            border-left: 5px solid #f97316;
        }
        .rule-card-blue {
            background: #eff6ff;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.75rem 0;
            border-left: 5px solid #0284c7;
        }
        .rule-card-green {
            background: #f0fdf4;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.75rem 0;
            border-left: 5px solid #16a34a;
        }
        .stats-card-orange {
            background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 3px solid #f97316;
            box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.2);
        }
        .stats-card-blue {
            background: linear-gradient(135deg, #eff6ff 0%, #bfdbfe 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 3px solid #0284c7;
            box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.2);
        }
        .stats-card-green {
            background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 3px solid #16a34a;
            box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2);
        }
        .stats-count {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .stats-label {
            font-size: 1rem;
            font-weight: 600;
        }
        .book-header-orange {
            background: #fff7ed;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0 1rem 0;
            border-left: 5px solid #f97316;
        }
        .book-header-orange h4 {
            margin: 0;
            color: #9a3412;
            font-size: 1.2rem;
        }
        .book-header-blue {
            background: #eff6ff;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0 1rem 0;
            border-left: 5px solid #0284c7;
        }
        .book-header-blue h4 {
            margin: 0;
            color: #0c4a6e;
            font-size: 1.2rem;
        }
        .book-header-green {
            background: #f0fdf4;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0 1rem 0;
            border-left: 5px solid #16a34a;
        }
        .book-header-green h4 {
            margin: 0;
            color: #14532d;
            font-size: 1.2rem;
        }
        .info-box {
            background: #eff6ff;
            border-left: 5px solid #0284c7;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            color: #0c4a6e;
            font-size: 1rem;
        }
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid #e5e7eb;
        }
        .stDownloadButton > button {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: white;
            border: none;
            font-size: 1.1rem;
            font-weight: 700;
            padding: 1rem;
            border-radius: 12px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Load logo
    logo_url = load_logo()
    
    # Navigation Bar
    if logo_url:
        st.markdown(f"""
            <div class="nav-bar">
                <div class="logo-container">
                    <img src="{logo_url}" class="logo-image" alt="Logo">
                    <div>
                        <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                        <p class="nav-subtitle">Book Segregation</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="nav-bar">
                <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                <p class="nav-subtitle">Book Segregation</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Back button
    col_back, col_space = st.columns([1.5, 5.5])
    with col_back:
        if st.button("← Back to Workspace", use_container_width=True, key="back_to_workspace_btn", type="secondary"):
            go_back_to_workspace()
    
    # Check for data availability
    if st.session_state.get("processed_df") is not None:
        df = st.session_state.processed_df
        data_source = "processed data"
    elif st.session_state.get("df_original") is not None:
        df = st.session_state.df_original
        data_source = "original data"
    else:
        st.error("No data available. Please return to home and upload a file.")
        st.stop()
    
    # Info banner
    st.markdown(f"""
        <div class="info-box">
            Segregating {data_source} with <strong>{len(df):,} rows</strong> into Cash Disbursement, Cash Receipts, and General Journal
        </div>
    """, unsafe_allow_html=True)
    
    # Classification Rules
    with st.expander("Classification Rules", expanded=False):
        st.markdown("""
            <div class="rule-card-orange">
                <strong style="color: #9a3412;">Cash Disbursement</strong>
                <p style="margin: 0.5rem 0 0 0; color: #7c2d12;">
                Bank accounts (RCBC, Westpac) with credit entries<br>
                Accounts Payable with debit entries
                </p>
            </div>
            
            <div class="rule-card-blue">
                <strong style="color: #0c4a6e;">Cash Receipts</strong>
                <p style="margin: 0.5rem 0 0 0; color: #1e40af;">
                Bank accounts (RCBC, Westpac) with debit entries<br>
                Accounts Receivable with credit entries
                </p>
            </div>
            
            <div class="rule-card-green">
                <strong style="color: #14532d;">General Journal</strong>
                <p style="margin: 0.5rem 0 0 0; color: #065f46;">
                Manual entries (date ending with "- Manual")<br>
                All other transactions
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Perform segregation
    try:
        classifier = BookCategoryClassifier()
        segregated = classifier.segregate(df)
        
        st.success("Data successfully segregated")
        
        # Statistics Summary
        st.markdown('<div class="section-header-orange">Summary Statistics</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cd_count = len(segregated["Cash Disbursement"])
            st.markdown(f"""
                <div class="stats-card-orange">
                    <div class="stats-count" style="color: #9a3412;">{cd_count:,}</div>
                    <div class="stats-label" style="color: #7c2d12;">Cash Disbursement</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            cr_count = len(segregated["Cash Receipts"])
            st.markdown(f"""
                <div class="stats-card-blue">
                    <div class="stats-count" style="color: #0c4a6e;">{cr_count:,}</div>
                    <div class="stats-label" style="color: #1e40af;">Cash Receipts</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            gj_count = len(segregated["General Journal"])
            st.markdown(f"""
                <div class="stats-card-green">
                    <div class="stats-count" style="color: #14532d;">{gj_count:,}</div>
                    <div class="stats-label" style="color: #065f46;">General Journal</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("---")
        st.write("")
        
        # Display each book
        st.markdown('<div class="section-header-orange">Cash Disbursement Book</div>', unsafe_allow_html=True)
        cd_df = segregated["Cash Disbursement"]
        if len(cd_df) > 0:
            st.dataframe(cd_df, height=min(400, len(cd_df) * 35 + 38), use_container_width=True)
        else:
            st.info("No transactions in this category")
        
        st.write("")
        st.markdown('<div class="section-header-blue">Cash Receipts Book</div>', unsafe_allow_html=True)
        cr_df = segregated["Cash Receipts"]
        if len(cr_df) > 0:
            st.dataframe(cr_df, height=min(400, len(cr_df) * 35 + 38), use_container_width=True)
        else:
            st.info("No transactions in this category")
        
        st.write("")
        st.markdown('<div class="section-header-green">General Journal Book</div>', unsafe_allow_html=True)
        gj_df = segregated["General Journal"]
        if len(gj_df) > 0:
            st.dataframe(gj_df, height=min(400, len(gj_df) * 35 + 38), use_container_width=True)
        else:
            st.info("No transactions in this category")
        
        # Download section at bottom
        st.write("")
        st.markdown("---")
        st.write("")
        
        # Create Excel file for download
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            segregated["Cash Disbursement"].to_excel(writer, sheet_name="Cash Disbursement", index=False)
            segregated["Cash Receipts"].to_excel(writer, sheet_name="Cash Receipts", index=False)
            segregated["General Journal"].to_excel(writer, sheet_name="General Journal", index=False)
        
        # Generate filename
        original = st.session_state.get("original_filename", "Excel_File.xlsx")
        base = re.sub(r"\.xlsx?$", "", original, flags=re.IGNORECASE)
        output_name = f"{base}_Segregated.xlsx"
        
        # Download button
        st.download_button(
            label=f"Download {output_name}",
            data=buffer.getvalue(),
            file_name=output_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
        
    except ValueError as e:
        st.error(f"Error: {str(e)}")
        st.info("Ensure your file contains: Journal ID, Account, Debit, and Credit columns")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")