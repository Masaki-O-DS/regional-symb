# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a neighborhood association (町内会) management system built with Streamlit frontend and FastAPI backend. The application manages community events, bulletin boards, inventory, financial reports, and meeting minutes.

## Architecture

**Frontend (Streamlit):**
- Main entry point: `frontend/app.py` - multi-page Streamlit app with sidebar navigation
- Module-based pages in `frontend/modules/` directory:
  - `dashboard.py` - Main dashboard
  - `event_calendar.py` - Event management
  - `kairanban.py` - Bulletin board system
  - `stock_list.py` - Inventory management
  - `financial_report.py` - Financial tracking
  - `meeting.py` - Meeting minutes
  - `chat.py` - Community chat
  - `admin.py` - Admin functions
- Shared utilities: `frontend/modules/func.py` - JSON data handling functions

**Backend (JSON Storage):**
- Data storage: JSON files in `backend/app/db/` directory (no API server required)

**Data Management:**
- JSON-based data storage with specialized handling for different file formats
- `event.json` uses `{"events": [...]}` structure, others use direct arrays
- Utility functions in `func.py` handle CRUD operations with automatic ID generation

## Common Commands

**Development:**
```bash
# Run Streamlit frontend (from project root)
streamlit run frontend/app.py

# Install dependencies (using rye)
rye sync
```

**Package Management:**
- Project uses `rye` for dependency management
- Dependencies defined in `pyproject.toml`
- Lock files: `requirements.lock` and `requirements-dev.lock`

## Key Dependencies

- **Frontend:** streamlit, streamlit-calendar, pandas, matplotlib, numpy
- **Data:** JSON file-based storage system with no backend API required
- **Validation:** pydantic, email-validator (for frontend data validation)

## Data Structure Notes

- All data files use JSON format with consistent ID-based indexing
- `func.py` provides unified CRUD operations across all modules
- Special handling for `event.json` which wraps events in an object structure
- Automatic ID generation ensures unique identifiers across all data types