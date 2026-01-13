"""
Utility functions module for the Excel Duplicate Delete application.

This module contains helper functions for various operations including:
- Data processing and manipulation
- File handling and conversion
- UI utility functions
- Business logic helpers
- Error handling utilities

All functions here are designed to be reusable and independent of specific
UI components to maintain separation of concerns.
"""

import pandas as pd
import openpyxl
from io import BytesIO
import base64
from pathlib import Path
import streamlit as st


def load_logo(logo_path=None):
    """
    Load and encode the logo image as base64 for display in Streamlit.
    
    Args:
        logo_path (Path, optional): Path to the logo image file. 
                                   If None, uses default path from config.
    
    Returns:
        str or None: Base64 encoded image string or None if file doesn't exist
    """
    if logo_path is None:
        logo_path = Path(r"C:\Users\Aaron Carl\bmg-finance-automation\images\logo.png")
    
    try:
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{logo_data}"
        else:
            return None
    except Exception as e:
        st.error(f"Error loading logo: {e}")
        return None


def get_rows_to_delete_logic(df, search_term):
    """
    Comprehensive logic to find rows that should be deleted based on search criteria.
    
    Logic:
    Step 1: Identify all rows containing the search term (case-sensitive matching)
    Step 2: Check each matched row's subsequent row for "Total" keyword (case-insensitive)
    Step 3: If "Total" is found in the next row, mark it for deletion as well
    
    Args:
        df (pandas.DataFrame): The source dataframe to search
        search_term (str): The exact text to search for (case-sensitive)
    
    Returns:
        list: Sorted list of row indices to be deleted
    """
    if not search_term:
        return []

    # Step 1: Locate all rows containing the search term with exact case matching
    mask = df.astype(str).apply(
        lambda column: column.str.contains(search_term, case=True, na=False)
    ).any(axis=1)
    
    matched_indices = df[mask].index.tolist()
    
    # Initialize the deletion set with matched indices
    final_deletion_set = set(matched_indices)
    
    # Step 2: Check for "Total" rows immediately following matched rows
    for idx in matched_indices:
        # Ensure we don't go beyond the dataframe bounds
        if idx + 1 < len(df):
            next_row = df.iloc[idx + 1]
            # Convert row to string and check for "total" (case-insensitive)
            row_content = str(next_row.values).lower()
            if "total" in row_content:
                final_deletion_set.add(idx + 1)

    return sorted(list(final_deletion_set))


def process_excel_with_formatting(uploaded_file, indices_to_delete):
    """
    Process Excel file using OpenPyXL to preserve all formatting while deleting rows.
    
    This function maintains:
    - Cell formatting (colors, fonts, borders)
    - Column widths
    - Row heights
    - Merged cells
    - Formulas
    - Data validation
    
    Args:
        uploaded_file: The uploaded Excel file object
        indices_to_delete (list): List of pandas indices to delete (0-based)
    
    Returns:
        bytes: The processed Excel file as bytes
    """
    # Reset file pointer to beginning
    uploaded_file.seek(0)
    
    # Load workbook with all formatting preserved
    workbook = openpyxl.load_workbook(uploaded_file)
    worksheet = workbook.active
    
    # Convert pandas indices (0-based) to Excel row numbers (1-based, accounting for header)
    # Pandas index 0 corresponds to Excel row 2 (row 1 is the header)
    excel_rows_to_delete = [pandas_index + 2 for pandas_index in indices_to_delete]
    
    # Sort in reverse order to delete from bottom to top
    # This prevents row number shifting issues during deletion
    excel_rows_to_delete.sort(reverse=True)
    
    # Delete each row
    for row_number in excel_rows_to_delete:
        worksheet.delete_rows(row_number)
    
    # Save the modified workbook to a BytesIO buffer
    output_buffer = BytesIO()
    workbook.save(output_buffer)
    
    return output_buffer.getvalue()


def apply_row_highlighting(row, deletion_queue=None, current_matches=None):
    """
    Apply color highlighting to dataframe rows for visualization.
    
    Args:
        row: A pandas Series representing a dataframe row
        deletion_queue (set): Set of row indices in deletion queue
        current_matches (list): List of row indices from current search
    
    Returns:
        list: List of CSS styles for each cell in the row
    """
    if deletion_queue is None:
        deletion_queue = set()
    if current_matches is None:
        current_matches = []
    
    if row.name in deletion_queue:
        return ['background-color: #fee2e2; border-left: 3px solid #dc2626'] * len(row)
    elif row.name in current_matches:
        return ['background-color: #fef9c3; border-left: 3px solid #eab308'] * len(row)
    else:
        return [''] * len(row)


def get_queue_statistics(df_original, deletion_queue):
    """
    Calculate statistics for the deletion queue.
    
    Args:
        df_original (DataFrame): Original dataframe
        deletion_queue (set): Set of row indices marked for deletion
    
    Returns:
        dict: Dictionary containing various statistics
    """
    original_row_count = len(df_original)
    rows_to_delete = len(deletion_queue)
    final_row_count = original_row_count - rows_to_delete
    
    return {
        'original_rows': original_row_count,
        'rows_to_delete': rows_to_delete,
        'final_rows': final_row_count
    }