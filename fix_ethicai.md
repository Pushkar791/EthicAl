# EthicAI Database & Error Handling Fix Guide

This guide provides step-by-step instructions to resolve the database issues in the EthicAI application. Follow these steps in order to fix the application.

## 1. Fix the Database Schema

First, run the script to fix the database schema issues:

```
python fix_database.py
```

This script will:
- Add missing columns (`visualizations`, `explainability` to `bias_report`)
- Add missing columns (`action_items` to `bias_recommendation`)
- Ensure all tables exist, including `assistant_interaction`
- Initialize any existing records with empty JSON values for new columns
- Provide diagnostic information about your current database

## 2. Improve Error Handling

Next, run the script to add error handling to critical code paths:

```
python fix_error_handling.py
```

This script will:
- Add safer attribute access using `getattr(obj, "attr", default_value)` pattern
- Wrap database operations in try-except blocks to prevent crashes
- Update the models.py file to provide safer defaults for JSON columns

## 3. Check Module Consistency

Run the script to check and fix module consistency:

```
python check_module_consistency.py
```

This script will:
- Check for potential issues in how modules interact with models
- Create test data to validate the models work correctly
- Test access to all critical model attributes
- Provide a report on any remaining issues

## 4. Restart the Application

After making these changes, restart the Flask application:

```
python run.py
```

## Troubleshooting

If you still encounter issues:

1. Check the terminal output for specific error messages
2. Look for any remaining database inconsistencies
3. Try accessing different sections of the application:
   - Bias Analyzer
   - Virtual Assistant
   - Governance
   - Learning Hub

For persistent issues, you may need to recreate the database from scratch:

```python
# Run this in a Python terminal
from app import create_app, db
app = create_app()
with app.app_context():
    db.drop_all()  # WARNING: This deletes all data
    db.create_all()  # Create fresh tables
```

## Understanding the Fixes

The key issues in the application were:

1. **Missing Database Columns**: The models had been updated with new fields, but the database schema was not updated to match.

2. **Error Handling**: The code was accessing these new fields without proper error handling, causing crashes when the columns didn't exist.

3. **Initialization**: New JSON columns weren't being properly initialized with default values.

The fixes ensure schema consistency and add robust error handling to prevent crashes in the future. 