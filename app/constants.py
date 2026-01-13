"""
Constants module for the Excel Duplicate Delete application.

This module defines all constant values used throughout the application,
including CSS styling, UI labels, help texts, and other static values.
Using constants ensures consistency and makes it easier to update values
across the entire application.

The constants are organized by category for better maintainability.
"""

# CSS STYLESHEET CONTENT
CSS_STYLES = """
    <style>
    /* ==================== GOOGLE FONTS IMPORT ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* ==================== GLOBAL STYLES ==================== */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background-color: #f5f7fa;
    }
    /* ===================== Responsive Screen ================ */ 

    .main, .content-wrapper {
    padding-left: clamp(1rem, 4vw, 3rem)
    padding-right: clamp(1rem, 4vw, 3rem)
    }

    @media(max-width: 768px){
    .nav-bar, .app-bar {
    padding: 1.5rem;
    }
     .app-bar h1 {
     font-size: 1.8rem;
     }

     .dataframe{
     overflow-x: auto;

     }
  }


    /* =====================  Mobile View ================ */ 

  @media (max-width: 640px){
  .nav-bar {
  flex-direction: column;
  align-center: flex-start;
  gap: 1rem;
  }
   .nav-title {
   font-size: 1.4rem;
   }

   .nav-subtitle{
   font-size: 0.85rem;
   }

   .stButton > button, 
   .stDownloadButton > button {
   width: 100%;
   font-size: 0.95rem;
   padding: 0.75rem 1rem;
}
.stTextInput > div > div > input {
    font-size: 0.95rem;
    
}

  }   

    
    /* ==================== LOGO STYLES ==================== */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-image {
        height: 110px;
        width: auto;
        object-fit: contain;
    }
    
    .logo-text {
        display: flex;
        flex-direction: column;
    }
    
    /* ==================== NAVIGATION BAR STYLES ==================== */
    .nav-bar {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e8ba3 100%);
        padding: 1.5rem 3rem;
        margin: -6rem -6rem 0rem -6rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-bar::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .nav-left {
        position: relative;
        z-index: 1;
    }
    
    .nav-right {
        position: relative;
        z-index: 1;
    }
    
    .nav-title {
        color: #ffffff;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    
    .nav-subtitle {
        color: rgba(255, 255, 255, 0.85);
        margin: 0.25rem 0 0 0;
        font-size: 0.95rem;
        font-weight: 400;
    }
    
    .nav-link {
        color: #ffffff;
        text-decoration: none;
        font-size: 1rem;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        display: inline-block;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* ==================== APPLICATION BAR STYLES ==================== */
    .app-bar {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e8ba3 100%);
        padding: 2rem 3rem;
        margin: -6rem -6rem 0rem -6rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .app-bar::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .app-bar-content {
        position: relative;
        z-index: 1;
    }
    
    .app-bar h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .app-bar p {
        color: rgba(255, 255, 255, 0.95);
        margin: 0.75rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* ==================== CENTER UPLOAD SECTION ==================== */
    .upload-container {
        max-width: 800px;
        margin: 4rem auto;
        padding: 0 2rem;
    }
    
    .upload-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 3.5rem 3rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        text-align: center;
        border: 1px solid #e8ecef;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .upload-header {
        color: #1e3c72;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        letter-spacing: -0.3px;
    }
    
    .upload-subheader {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    .upload-instructions {
        background: #f8fafc;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 3rem;
        border-left: 4px solid #2a5298;
    }
    
    .upload-instructions h3 {
        color: #1e3c72;
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    .instruction-list {
        text-align: left;
        color: #475569;
        line-height: 1.9;
        font-size: 1rem;
    }
    
    .instruction-list li {
        margin-bottom: 0.75rem;
        padding-left: 0.5rem;
    }
    
    .instruction-step {
        font-weight: 600;
        color: #2a5298;
    }
    
    /* ==================== MAIN CONTENT SECTIONS ==================== */
    .content-wrapper {
        padding: 2.5rem 3rem;
        margin: 0 -6rem;
        background: #f5f7fa;
    }
    
    .section-header {
        color: #1e3c72;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* ==================== INPUT AND FORM ELEMENTS ==================== */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2a5298;
        box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* ==================== BUTTON STYLES ==================== */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(42, 82, 152, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        box-shadow: 0 6px 20px rgba(42, 82, 152, 0.3);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(42, 82, 152, 0.2);
    }
    
    /* ==================== DOWNLOAD BUTTON SPECIAL STYLE ==================== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 6px 20px rgba(5, 150, 105, 0.3);
        transform: translateY(-2px);
    }
    
    /* ==================== ALERT AND MESSAGE BOXES ==================== */
    .stSuccess {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        color: #065f46;
    }
    
    .stWarning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        color: #92400e;
    }
    
    .stInfo {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        color: #1e40af;
    }
    
    /* ==================== DATAFRAME STYLING ==================== */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    /* ==================== FILE UPLOADER STYLING ==================== */
    .stFileUploader {
        background: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #2a5298;
        background: #f8fafc;
    }
    
    .stFileUploader > div > div {
        text-align: center;
    }
    
    /* ==================== FOOTER STYLES ==================== */
    .footer {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e8ba3 100%);
        padding: 3rem 3rem 2.5rem 3rem;
        margin: 4rem -6rem -6rem -6rem;
        text-align: center;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .footer-content {
        position: relative;
        z-index: 1;
    }
    
    .footer-title {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        letter-spacing: 0.3px;
    }
    
    .footer-description {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0;
        font-size: 1rem;
        font-weight: 400;
    }
    
    .footer-features {
        color: rgba(255, 255, 255, 0.85);
        margin: 1rem 0;
        font-size: 0.95rem;
        font-weight: 400;
    }
    
    .footer-separator {
        width: 60px;
        height: 2px;
        background: rgba(255, 255, 255, 0.3);
        margin: 1.5rem auto;
    }
    
    .footer-copyright {
        color: rgba(255, 255, 255, 0.7);
        margin-top: 1.5rem;
        font-size: 0.9rem;
        font-weight: 400;
    }
    
    /* ==================== HIDE STREAMLIT BRANDING ==================== */
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    header {
        visibility: hidden;
    }
    
    /* ==================== RESPONSIVE ADJUSTMENTS ==================== */
    @media (max-width: 768px) {
        .app-bar, .nav-bar {
            padding: 1.5rem 1.5rem;
        }
        
        .app-bar h1 {
            font-size: 1.8rem;
        }
        
        .upload-card {
            padding: 2rem 1.5rem;
        }
        
        .upload-header {
            font-size: 1.6rem;
        }
        
        .logo-image {
            height: 40px;
        }
    }
    
    /* ==================== SPINNER CUSTOMIZATION ==================== */
    .stSpinner > div {
        border-top-color: #2a5298;
    }
    
    /* ==================== DIVIDER STYLING ==================== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
        margin: 2rem 0;
    }
    .suggestion-container {
        margin: 0.5rem 0 1rem 0;
        padding: 0.75rem;
        background: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .suggestion-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 0.5rem;
    }
    
    .suggestion-button {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
    }
    
    .suggestion-button:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
        transform: translateY(-1px);
    }
    </style>
"""

# UI LABELS AND TEXTS
UI_LABELS = {
    # Home page
    'APP_DESCRIPTION': 'Efficiently identify and remove duplicate rows while preserving all formatting and styles',
    'UPLOAD_HEADER': 'Get Started',
    'UPLOAD_SUBHEADER': 'Upload your Excel file to begin the duplicate removal process',
    'PROCEED_BUTTON': 'Proceed to Workspace',
    
    # How it works instructions
    'HOW_IT_WORKS_TITLE': 'How It Works',
    'INSTRUCTION_STEP_1': 'Upload File',
    'INSTRUCTION_DESC_1': 'Select your Excel file (.xlsx or .xls format)',
    'INSTRUCTION_STEP_2': 'Search Duplicates',
    'INSTRUCTION_DESC_2': 'Enter exact text to find duplicate rows (case-sensitive matching)',
    'INSTRUCTION_STEP_3': 'Build Queue',
    'INSTRUCTION_DESC_3': 'Add matching rows to your deletion queue for review',
    'INSTRUCTION_STEP_4': 'Review & Rescue',
    'INSTRUCTION_DESC_4': 'Examine queued rows and rescue any that should be kept',
    'INSTRUCTION_STEP_5': 'Download',
    'INSTRUCTION_DESC_5': 'Export your cleaned Excel file with all original formatting preserved',
    
    # Workspace page
    'WORKSPACE_SUBTITLE': 'Workspace - Process Your Data',
    'BACK_TO_HOME': '← Back to Home',
    'STEP_1_HEADER': 'Step 1: Find and Add to Queue',
    'SEARCH_PLACEHOLDER': 'Enter exact text to search for...',
    'ADD_TO_QUEUE_BUTTON': 'Add {count} Row(s) to Deletion Queue',
    'ORIGINAL_DATA_PREVIEW': 'Original Data Preview',
    'LEGEND_RED': 'Red = In Queue',
    'LEGEND_YELLOW': 'Yellow = Current Match',
    
    # Step 2 - Queue Management
    'STEP_2_HEADER': 'Step 2: Review Deletion Queue',
    'QUEUE_STATUS': 'Total Rows Queued for Deletion: {count}',
    'ROWS_MARKED_FOR_DELETION': 'Rows Marked for Deletion:',
    'RESCUE_ROW': 'Rescue Row',
    'SELECT_ROW_TO_RESCUE': 'Select Excel Row to Keep:',
    'RESCUE_HELP': 'Choose a row number to remove it from the deletion queue',
    'RESCUE_BUTTON': 'Rescue Selected Row',
    'RESET_QUEUE': 'Reset Queue',
    'CLEAR_QUEUE_BUTTON': 'Clear Entire Queue',
    'EMPTY_QUEUE_MESSAGE': 'Deletion queue is empty. Search for duplicates and add rows to get started.',
    
    # Step 3 - Preview and Download
    'STEP_3_HEADER': 'Step 3: Preview and Download',
    'FINAL_RESULT_PREVIEW': 'Preview of Final Result',
    'CONFIRM_AND_DOWNLOAD': 'Confirm Deletion and Download Excel',
    'DOWNLOAD_BUTTON': 'Download Cleaned Excel File',
    'NO_ROWS_MESSAGE': 'Add rows to the deletion queue to enable download.',
    
    # Footer
    'FOOTER_TITLE': 'Excel Duplicate Delete Tool',
    'FOOTER_DESCRIPTION': 'A professional solution for managing duplicate data in Excel spreadsheets',
    'FOOTER_FEATURES': 'Preserves Formatting • Case-Sensitive Search • Smart Total Detection • Batch Processing',
    'FOOTER_COPYRIGHT': 'Built for BMG Outsourcing INC.'
}

# HELP TEXTS
HELP_TEXTS = {
    'SEARCH_INPUT': 'Search is case-sensitive. For example, \'Apple\' will not match \'apple\'.',
    'FILE_UPLOADER': 'Select your Excel file (.xlsx or .xls format)'
}

# COLOR CODES
COLOR_CODES = {
    'RED_HIGHLIGHT': '#fee2e2',
    'YELLOW_HIGHLIGHT': '#fef9c3',
    'RED_BORDER': '#dc2626',
    'YELLOW_BORDER': '#eab308'
}