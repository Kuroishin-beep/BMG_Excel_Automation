# BMG Excel Automation (Excel Duplicate Cleaner)

BMG Excel Automation is a clean, interactive Streamlit application designed for efficiently managing and cleaning Excel files by handling duplicates. It provides an easy-to-use graphical interface to view, filter, and selectively eliminate duplicate rows without losing your original Excel formatting.

## Features

* **File Upload & Parsing:** Easily attach and view any `.xlsx` Excel file.
* **Instant Preview:** The system automatically reads the file and displays all rows and columns in a structured table.
* **Interactive Search Filter:** Type in specific items to search, and the application will immediately highlight matching data.
* **Duplicate Review:** Review all rows containing identical and duplicate information.
* **Action Selector:** Choose how to handle duplicates:
  * **Keep one row:** Retain only a single instance of the duplicate and remove the rest.
  * **Delete all rows:** Completely remove all rows that have identical content.
* **Live Updates:** Selected changes are applied instantly.
* **Seamless Download:** Export the updated Excel file, keeping the same file name and formatting, with all applied data updates.

## Prerequisites

Ensure you have Python 3.8 or newer installed. The main dependencies are:
* Streamlit
* Pandas
* Openpyxl

You can find the full list of required libraries in `requirements.txt`.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Kuroishin-beep/BMG_Excel_Automation.git
cd BMG_Excel_Automation
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment before installing packages.
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit application by running the following command:
```bash
streamlit run app/main.py
```

## How to Use

1. Launch the application to open the interface in your web browser.
2. Click to **Upload an Excel file** to the system.
3. Review the data displayed on the screen.
4. Use the **search filter** to look for specific items.
5. Review the duplicate groups shown on the screen.
6. Choose an action for each duplicate group (e.g., Keep one, Delete all).
7. Apply your changes.
8. Click **Download** to get the updated, duplicate-free version of your Excel file.
