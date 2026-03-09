"""
Workspace page module for the Excel Duplicate Delete application.

Simplified version: auto-deletes all rows containing "Reversed" (case-insensitive),
shows before/after preview, and allows download of cleaned file.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import re
from io import BytesIO

sys.path.append(str(Path(__file__).parent.parent))

from utils import load_logo
from constants import UI_LABELS, COLOR_CODES
from config import AppConfig


def go_to_home():
    """Navigate back to home page and reset state."""
    st.session_state.current_page = 'home'
    st.session_state.df_original = None
    st.session_state.deletion_queue = set()
    st.session_state.current_matches = []
    st.session_state.uploaded_file = None
    st.session_state.original_filename = None
    if 'processed_df' in st.session_state:
        del st.session_state.processed_df
    if 'processed_file_data' in st.session_state:
        del st.session_state.processed_file_data


def go_to_segregation():
    """Navigate to segregation page with processed data."""
    df = st.session_state.df_original
    reversed_indices = get_reversed_indices(df)

    if reversed_indices:
        st.session_state.processed_df = df.drop(reversed_indices, errors='ignore')
    else:
        st.session_state.processed_df = df.copy()

    st.session_state.current_page = 'segregation'
    st.rerun()


def get_reversed_indices(df):
    """
    Return list of row indices that belong to 'Reversed/Reversal' journal groups.

    A journal group starts with a section-header row whose first column matches
    "ID XXXXXX Reversed..." or "ID XXXXXX ... Reversal...".
    Only groups whose HEADER contains Reversed/Reversal are removed — individual
    transaction lines inside a normal group that happen to mention 'reversal'
    (e.g. 'Unpaid/Lates Reversal') are intentionally ignored.

    Each matched group spans from its header row through the closing 'Total' row
    and the blank separator that follows.
    """
    first_col = df.columns[0]
    all_indices = df.index.tolist()

    expanded = set()

    for pos, idx in enumerate(all_indices):
        cell_val = str(df.iloc[pos][first_col]).strip()

        # Only trigger on section-header rows: "ID <number> ... Reversed/Reversal ..."
        if re.match(r"^ID\s+\d+", cell_val, re.IGNORECASE) and \
           re.search(r"revers(ed|al)", cell_val, re.IGNORECASE):

            group_start_pos = pos

            # Walk forward to find the closing 'Total' row (+ trailing blank)
            group_end_pos = pos
            for fwd in range(pos, min(pos + 100, len(all_indices))):
                fwd_val = str(df.iloc[fwd][first_col]).strip().lower()
                if fwd_val == "total":
                    group_end_pos = fwd
                    if fwd + 1 < len(all_indices):
                        group_end_pos = fwd + 1
                    break

            for p in range(group_start_pos, group_end_pos + 1):
                expanded.add(all_indices[p])

    return sorted(list(expanded))


def highlight_reversed(row, reversed_set):
    """Apply red highlight to rows marked for deletion."""
    if row.name in reversed_set:
        return [f'background-color: {COLOR_CODES["RED_HIGHLIGHT"]}'] * len(row)
    return [''] * len(row)


def render_workspace_page():
    """
    Render the simplified workspace page.

    Shows:
    - Left column: Original data with reversed rows highlighted in red
    - Right column: Cleaned data preview (reversed rows removed)
    - Download button for the cleaned file
    """

    if 'show_modal' not in st.session_state:
        st.session_state.show_modal = False

    # --- CSS ---
    st.markdown("""
        <style>
        .nav-bar {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .nav-title  { color: white !important; font-size: 1.8rem; font-weight: 700; margin: 0; }
        .nav-subtitle { color: white !important; font-size: 1rem; margin: 0.25rem 0 0 0; }
        .logo-container { display: flex; align-items: center; gap: 1rem; }
        .logo-image { height: 50px; width: auto; }

        .section-header-red {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white; padding: 1rem 1.5rem; border-radius: 12px;
            font-size: 1.3rem; font-weight: 700; text-align: center;
            margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(220,38,38,0.3);
        }
        .section-header-green {
            background: linear-gradient(135deg, #16a34a 0%, #4ade80 100%);
            color: white; padding: 1rem 1.5rem; border-radius: 12px;
            font-size: 1.3rem; font-weight: 700; text-align: center;
            margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(22,163,74,0.3);
        }

        .info-box-red {
            background: #fef2f2; border-left: 5px solid #dc2626;
            padding: 1rem; border-radius: 8px; margin: 1rem 0;
            color: #7f1d1d; font-size: 1rem;
        }
        .info-box-green {
            background: #f0fdf4; border-left: 5px solid #16a34a;
            padding: 1rem; border-radius: 8px; margin: 1rem 0;
            color: #14532d; font-size: 1rem;
        }

        .stats-box {
            background: white; border: 2px solid #e5e7eb; border-radius: 12px;
            padding: 1.25rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stat-row {
            display: flex; justify-content: space-between;
            padding: 0.75rem 0; border-bottom: 1px solid #f3f4f6; font-size: 1.05rem;
        }
        .stat-row:last-child { border-bottom: none; }
        .stat-label { color: #6b7280; font-weight: 600; }
        .stat-value { color: #1f2937; font-weight: 700; }

        .legend-container {
            background: white; border: 2px solid #e5e7eb;
            border-radius: 12px; padding: 1rem; margin-top: 1rem;
        }
        .legend-title { font-weight: 700; color: #374151; margin-bottom: 0.5rem; font-size: 1rem; }
        .legend-item {
            display: inline-block; padding: 4px 12px; border-radius: 6px;
            margin: 0 8px 8px 0; font-size: 0.95rem; font-weight: 500;
        }

        .stButton > button {
            border-radius: 10px; font-weight: 600; font-size: 1rem;
            padding: 0.75rem 1.5rem; transition: all 0.2s;
        }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .stDownloadButton > button {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: white; border: none; font-size: 1.1rem;
            font-weight: 700; padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Nav Bar ---
    logo_url = load_logo()
    if logo_url:
        st.markdown(f"""
            <div class="nav-bar">
                <div class="logo-container">
                    <img src="{logo_url}" class="logo-image" alt="Logo">
                    <div>
                        <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                        <p class="nav-subtitle">{UI_LABELS['WORKSPACE_SUBTITLE']}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="nav-bar">
                <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                <p class="nav-subtitle">{UI_LABELS['WORKSPACE_SUBTITLE']}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- Book Segregation nav button ---
    col_segregate, col_space = st.columns([1.5, 5.5])
    with col_segregate:
        if st.button("📚 Book Segregation", use_container_width=True, key="direct_segregation_btn", type="secondary"):
            go_to_segregation()

    # --- Guard ---
    if st.session_state.df_original is None:
        st.error("No file loaded. Please return to home and upload a file.")
        st.stop()

    df = st.session_state.df_original

    # Cache keyed on filename — id(df) is unsafe because Python reuses memory
    # addresses, meaning a newly uploaded file can get the same id() as the old
    # one and incorrectly receive stale reversed_indices from the previous file.
    cache_key = st.session_state.get('original_filename', '__unknown__')
    if 'reversed_indices' not in st.session_state or st.session_state.get('_reversed_cache_key') != cache_key:
        st.session_state.reversed_indices = set(get_reversed_indices(df))
        st.session_state._reversed_cache_key = cache_key
        # Clear any stale processed file from a previous upload
        st.session_state.pop('processed_file_data', None)
        st.session_state.pop('processed_df', None)

    reversed_indices = st.session_state.reversed_indices
    df_cleaned = df.drop(list(reversed_indices), errors='ignore')

    # =========================================================
    # TWO-COLUMN LAYOUT: BEFORE  |  AFTER
    # =========================================================
    col_before, col_after = st.columns(2)

    # --- BEFORE (left) ---
    with col_before:
        st.markdown('<div class="section-header-red">Before: Original Data</div>', unsafe_allow_html=True)

        if reversed_indices:
            st.markdown(
                f'<div class="info-box-red">🗑️ {len(reversed_indices)} "Reversed/Reversal" '
                f'row{"s" if len(reversed_indices) != 1 else ""} will be removed</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="info-box-red">No "Reversed" or "Reversal" rows found in this file.</div>',
                unsafe_allow_html=True
            )

        try:
            styled = df.style.apply(
                lambda row: highlight_reversed(row, reversed_indices), axis=1
            )
            st.dataframe(styled, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)
        except Exception:
            st.dataframe(df, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)

        st.markdown(f"""
            <div class="legend-container">
                <div class="legend-title">Color Guide:</div>
                <span class="legend-item" style='background: {COLOR_CODES["RED_HIGHLIGHT"]};'>Reversed / Reversal — will be deleted</span>
            </div>
        """, unsafe_allow_html=True)

    # --- AFTER (right) ---
    with col_after:
        st.markdown('<div class="section-header-green">After: Cleaned Data & Download</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="info-box-green">✅ {len(df_cleaned)} row{"s" if len(df_cleaned) != 1 else ""} remaining after cleanup</div>',
            unsafe_allow_html=True
        )

        st.dataframe(df_cleaned, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)

        # Stats
        st.markdown(f"""
            <div class="stats-box">
                <div class="stat-row">
                    <span class="stat-label">Original Rows:</span>
                    <span class="stat-value">{len(df)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Reversed/Reversal Rows Removed:</span>
                    <span class="stat-value" style="color: #dc2626;">{len(reversed_indices)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Final Rows:</span>
                    <span class="stat-value" style="color: #16a34a;">{len(df_cleaned)}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.write("---")

        # Download button
        if reversed_indices:
            # Build the output filename
            original = st.session_state.get("original_filename", "Excel_File.xlsx")
            base = re.sub(r"\.xlsx?$", "", original, flags=re.IGNORECASE)
            output_name = f"{base}_Cleaned.xlsx"

            # Generate Excel bytes once and cache them
            if 'processed_file_data' not in st.session_state or st.session_state.get('_reversed_cache_key') != cache_key:
                buffer = BytesIO()
                with st.spinner("Generating Excel file..."):
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_cleaned.to_excel(writer, index=False)
                    st.session_state.processed_file_data = buffer.getvalue()
                    st.session_state.processed_df = df_cleaned

            processed_excel_data = st.session_state.processed_file_data

            st.download_button(
                label="📥 Download Cleaned Excel File",
                data=processed_excel_data,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update({'show_modal': True}),
            )
        else:
            st.markdown(
                '<div class="info-box-green">No "Reversed" or "Reversal" rows were found — nothing to clean up.</div>',
                unsafe_allow_html=True
            )