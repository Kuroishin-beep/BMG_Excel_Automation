"""
Pages package initialization for the Excel Duplicate Delete application.

This module makes the 'pages' directory a Python package, enabling
proper imports of individual page modules. It can contain shared
functionality for all pages if needed.

The pages package contains:
- home.py: The main landing page with file upload functionality
- workspace.py: The main processing page with search and queue management
- segregation.py: The segregation and book category classification page
- feedback.py: The user feedback submission page
"""

# Import page functions for easy access
try:
    from .home import render_home_page
except ImportError:
    render_home_page = None

try:
    from .workspace import render_workspace_page
except ImportError:
    render_workspace_page = None

try:
    from .segregation import render_segregation_page
except ImportError:
    render_segregation_page = None

try:
    from .feedback import render_feedback_page
except ImportError:
    render_feedback_page = None

# Define available pages mapping
AVAILABLE_PAGES = {
    'home': render_home_page,
    'workspace': render_workspace_page,
    'segregation': render_segregation_page,
    'feedback': render_feedback_page,
}

# Remove any None values if imports failed (e.g., if a file is missing during development)
AVAILABLE_PAGES = {k: v for k, v in AVAILABLE_PAGES.items() if v is not None}