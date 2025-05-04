from app import create_app, db
from app.models import BiasReport, BiasRecommendation, AIModel, AuditLog, AssistantInteraction
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    # Check all tables and their columns
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")
    
    # Check specific models that might cause issues
    try:
        # Check bias_report table
        print("\nChecking BiasReport records:")
        reports = BiasReport.query.limit(1).all()
        for report in reports:
            print(f"  - Report ID: {report.id}")
            print(f"    visualizations: {'Present' if report.visualizations is not None else 'None'}")
            print(f"    explainability: {'Present' if report.explainability is not None else 'None'}")
    except Exception as e:
        print(f"Error with BiasReport: {e}")
    
    try:
        # Check bias_recommendation table
        print("\nChecking BiasRecommendation records:")
        recommendations = BiasRecommendation.query.limit(1).all()
        for rec in recommendations:
            print(f"  - Recommendation ID: {rec.id}")
            print(f"    action_items: {'Present' if rec.action_items is not None else 'None'}")
    except Exception as e:
        print(f"Error with BiasRecommendation: {e}")
    
    try:
        # Check virtual assistant related tables
        print("\nChecking AssistantInteraction records:")
        interactions = AssistantInteraction.query.limit(1).all()
        print(f"  Found {len(interactions)} interactions")
    except Exception as e:
        print(f"Error with AssistantInteraction: {e}") 