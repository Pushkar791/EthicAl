from app import create_app, db
from app.models import BiasReport, BiasRecommendation, AssistantInteraction, AIModel
import os
import json
import re

app = create_app()

def check_modules_code():
    """Check the code in modules for potential model usage issues"""
    modules_dir = os.path.join('app', 'modules')
    issues = []
    
    # Define the patterns to check for
    patterns = {
        'bias_analyzer': [
            ('visualizations', BiasReport),
            ('explainability', BiasReport),
            ('action_items', BiasRecommendation)
        ],
        'virtual_assistant': [
            ('query', AssistantInteraction),
            ('response', AssistantInteraction),
            ('consent_given', AssistantInteraction)
        ]
    }
    
    # Check each module
    for module in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module)
        if os.path.isdir(module_path) and module in patterns:
            routes_file = os.path.join(module_path, 'routes.py')
            
            if os.path.exists(routes_file):
                with open(routes_file, 'r') as f:
                    content = f.read()
                
                for attribute, model in patterns[module]:
                    # Check for attribute access without proper error handling
                    usage_pattern = rf'{model.__name__}.*\.{attribute}'
                    if re.search(usage_pattern, content):
                        # Check if there's try/except around it
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if re.search(usage_pattern, line):
                                # Basic check for try/except around this line
                                has_try = any('try:' in lines[j] for j in range(max(0, i-5), i))
                                if not has_try:
                                    issues.append(f"Potential issue in {routes_file}, line ~{i+1}: "
                                                 f"Access to {model.__name__}.{attribute} without error handling")
    
    return issues

def create_test_data():
    """Create test data to validate the models"""
    try:
        # Create or get a test AI model
        test_model = AIModel.query.filter_by(name="Test Model").first()
        if not test_model:
            test_model = AIModel(
                name="Test Model",
                version="1.0",
                description="Test model for diagnostic purposes",
                model_type="classification",
                risk_level="low"
            )
            db.session.add(test_model)
            db.session.flush()
        
        # Create a bias report with all required fields
        test_report = BiasReport(
            report_type="gender",
            results=json.dumps({"test": "data"}),
            visualizations=json.dumps({"test_viz": "data"}),
            explainability=json.dumps({"test_explain": "data"}),
            ai_model_id=test_model.id
        )
        db.session.add(test_report)
        db.session.flush()
        
        # Create a bias recommendation with all required fields
        test_recommendation = BiasRecommendation(
            title="Test Recommendation",
            description="This is a test recommendation",
            priority="medium",
            action_items=json.dumps(["Test action 1", "Test action 2"]),
            report_id=test_report.id
        )
        db.session.add(test_recommendation)
        
        # Create an assistant interaction
        test_interaction = AssistantInteraction(
            query="Test query",
            response="Test response",
            consent_given=True
        )
        db.session.add(test_interaction)
        
        # Commit all changes
        db.session.commit()
        return True, "Test data created successfully"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error creating test data: {e}"

def test_model_functionality():
    """Test if models function correctly"""
    results = {}
    
    # Test BiasReport functionality
    try:
        report = BiasReport.query.first()
        if report:
            _ = report.visualizations  # Access the attribute
            _ = report.explainability  # Access the attribute
            results['bias_report'] = "Working"
        else:
            results['bias_report'] = "No reports found to test"
    except Exception as e:
        results['bias_report'] = f"Error: {e}"
    
    # Test BiasRecommendation functionality
    try:
        rec = BiasRecommendation.query.first()
        if rec:
            _ = rec.action_items  # Access the attribute
            results['bias_recommendation'] = "Working"
        else:
            results['bias_recommendation'] = "No recommendations found to test"
    except Exception as e:
        results['bias_recommendation'] = f"Error: {e}"
    
    # Test AssistantInteraction functionality
    try:
        interaction = db.session.query(AssistantInteraction).first()
        if interaction:
            _ = interaction.query  # Access the attribute
            _ = interaction.response  # Access the attribute
            results['assistant_interaction'] = "Working"
        else:
            results['assistant_interaction'] = "No interactions found to test"
    except Exception as e:
        results['assistant_interaction'] = f"Error: {e}"
    
    return results

if __name__ == "__main__":
    with app.app_context():
        print("--- Checking Module Consistency ---")
        issues = check_modules_code()
        if issues:
            print("\nPotential issues found:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("No potential code issues found in modules")
        
        print("\n--- Creating Test Data ---")
        success, message = create_test_data()
        print(message)
        
        if success:
            print("\n--- Testing Model Functionality ---")
            results = test_model_functionality()
            for model, status in results.items():
                print(f"{model}: {status}")
            
            print("\nIf all tests passed, your application should now be working correctly.")
            print("Please restart your Flask application with 'python run.py' and test it in the browser.") 