from app import create_app, db
from app.models import BiasReport, BiasRecommendation, AssistantInteraction, User, AIModel
from sqlalchemy import text, inspect
import json

app = create_app()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_column_if_not_exists(table_name, column_name, column_type):
    """Add a column to a table if it doesn't exist."""
    if not check_column_exists(table_name, column_name):
        print(f"Adding column {column_name} to table {table_name}")
        db.session.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'))
        return True
    else:
        print(f"Column {column_name} already exists in table {table_name}")
        return False

def fix_database():
    """Fix database schema to match models."""
    changes_made = False
    
    # Fix BiasReport table
    if add_column_if_not_exists('bias_report', 'visualizations', 'JSON'):
        changes_made = True
    if add_column_if_not_exists('bias_report', 'explainability', 'JSON'):
        changes_made = True
    
    # Fix BiasRecommendation table
    if add_column_if_not_exists('bias_recommendation', 'action_items', 'JSON'):
        changes_made = True
    
    # Check and initialize with empty JSON if needed
    try:
        # Update any existing BiasReport records
        reports = BiasReport.query.all()
        for report in reports:
            if report.visualizations is None:
                report.visualizations = json.dumps({})
            if report.explainability is None:
                report.explainability = json.dumps({})
                changes_made = True
        
        # Update any existing BiasRecommendation records
        recommendations = BiasRecommendation.query.all()
        for rec in recommendations:
            if rec.action_items is None:
                rec.action_items = json.dumps([])
                changes_made = True
    except Exception as e:
        print(f"Error updating existing records: {e}")
    
    # Check for missing tables
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    # Ensure all tables are created
    if 'assistant_interaction' not in tables:
        print("Creating missing table: assistant_interaction")
        db.create_all()
        changes_made = True
    
    # Ensure AssistantInteraction has the right columns
    for column_name, column_type in [
        ('query', 'TEXT'), 
        ('response', 'TEXT'),
        ('timestamp', 'DATETIME'),
        ('consent_given', 'BOOLEAN'),
        ('user_id', 'INTEGER')
    ]:
        if add_column_if_not_exists('assistant_interaction', column_name, column_type):
            changes_made = True
    
    # Regenerate tables if needed
    if changes_made:
        db.session.commit()
        print("Database schema updated successfully!")
    else:
        print("Database schema already up to date!")
    
    return changes_made

def diagnose_database():
    """Diagnose database schema and report any issues."""
    inspector = inspect(db.engine)
    
    # Print tables and their columns
    print("\n--- DATABASE SCHEMA DIAGNOSIS ---")
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")
    
    # Check specific models
    print("\n--- MODEL DIAGNOSIS ---")
    try:
        print(f"Users count: {User.query.count()}")
        print(f"AI Models count: {AIModel.query.count()}")
        print(f"Bias Reports count: {BiasReport.query.count()}")
        print(f"Bias Recommendations count: {BiasRecommendation.query.count()}")
        print(f"Assistant Interactions count: {AssistantInteraction.query.count()}")
    except Exception as e:
        print(f"Error querying model counts: {e}")
    
    # Try to create sample records to ensure models are working
    try:
        print("\n--- SAMPLE RECORD CREATION TEST ---")
        test_interaction = AssistantInteraction(
            query="Test query for diagnostic purposes",
            response="Test response for diagnostic purposes",
            consent_given=True,
            user_id=None  # No user for test record
        )
        db.session.add(test_interaction)
        db.session.flush()
        print(f"Successfully created test AssistantInteraction with ID: {test_interaction.id}")
        db.session.rollback()  # Don't actually save the test record
    except Exception as e:
        print(f"Error creating test interaction: {e}")

if __name__ == "__main__":
    with app.app_context():
        changes_made = fix_database()
        diagnose_database()
        
        if changes_made:
            print("\nRecommendation: Please restart your Flask application to apply changes.") 