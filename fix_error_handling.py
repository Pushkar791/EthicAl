import re
import os
from app import create_app

app = create_app()

def add_error_handling_to_routes():
    """Add proper error handling to routes that access potentially missing attributes"""
    modules_dir = os.path.join('app', 'modules')
    modified_files = []
    
    # Patterns to match in the code
    patterns = {
        'bias_analyzer': [
            (r'(report\.visualizations)', 'getattr(report, "visualizations", {})'),
            (r'(report\.explainability)', 'getattr(report, "explainability", {})'),
            (r'(recommendation\.action_items)', 'getattr(recommendation, "action_items", [])')
        ],
        'virtual_assistant': [
            (r'(interaction\.query)', 'getattr(interaction, "query", "")'),
            (r'(interaction\.response)', 'getattr(interaction, "response", "")')
        ]
    }
    
    # Process each module
    for module in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module)
        if os.path.isdir(module_path) and module in patterns:
            routes_file = os.path.join(module_path, 'routes.py')
            
            if os.path.exists(routes_file):
                with open(routes_file, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Perform replacements
                for pattern, replacement in patterns[module]:
                    # Avoid replacing patterns within try blocks
                    # This is a simplistic approach - may need refinement
                    lines = content.split('\n')
                    new_lines = []
                    in_try_block = False
                    
                    for line in lines:
                        if 'try:' in line:
                            in_try_block = True
                        elif in_try_block and 'except' in line:
                            in_try_block = False
                        
                        # Only replace if we're not in a try block
                        if not in_try_block and re.search(pattern, line):
                            new_line = re.sub(pattern, replacement, line)
                            new_lines.append(new_line)
                        else:
                            new_lines.append(line)
                    
                    content = '\n'.join(new_lines)
                
                # Add try-except blocks around model queries
                # This is more complex and would require careful AST parsing
                # For now, we'll focus on simple attribute access
                
                # Write back if changes were made
                if content != original_content:
                    with open(routes_file, 'w') as f:
                        f.write(content)
                    modified_files.append(routes_file)
                    print(f"Updated error handling in {routes_file}")
    
    return modified_files

def add_try_except_to_routes():
    """Add try-except blocks to database operations in routes"""
    modules_dir = os.path.join('app', 'modules')
    modified_files = []
    
    # Patterns to look for and wrap in try-except
    operations = [
        r'(\w+)\.query\.(\w+)\(',  # Model.query.method(
        r'db\.session\.(\w+)\(',  # db.session.method(
    ]
    
    # Process each module
    for module_name in ['bias_analyzer', 'virtual_assistant', 'governance', 'learning_hub']:
        module_path = os.path.join(modules_dir, module_name)
        if os.path.isdir(module_path):
            routes_file = os.path.join(module_path, 'routes.py')
            
            if os.path.exists(routes_file):
                with open(routes_file, 'r') as f:
                    lines = f.readlines()
                
                # Find areas that need try-except blocks
                updated_lines = []
                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    # Check if line contains a database operation pattern
                    needs_try_except = False
                    for pattern in operations:
                        if re.search(pattern, line) and not any(x in line for x in ['try:', 'except', 'with']):
                            # Check if we're already in a try block
                            # Check 5 lines backward
                            start_idx = max(0, i-5)
                            prev_code = ''.join(lines[start_idx:i])
                            if 'try:' not in prev_code:
                                needs_try_except = True
                                break
                    
                    if needs_try_except:
                        # Get indentation level
                        indent = re.match(r'^(\s*)', line).group(1)
                        
                        # Add try block
                        updated_lines.append(f"{indent}try:\n")
                        updated_lines.append(f"{indent}    {line.lstrip()}")
                        
                        # Look ahead for related lines to include in the try block
                        j = i + 1
                        end_j = j
                        while j < len(lines) and (lines[j].strip() == '' or 
                                                lines[j].startswith(indent + ' ') or 
                                                lines[j].startswith(indent + '\t')):
                            updated_lines.append(f"{indent}    {lines[j].lstrip()}")
                            end_j = j
                            j += 1
                        
                        # Add except block
                        updated_lines.append(f"{indent}except Exception as e:\n")
                        updated_lines.append(f"{indent}    print(f\"Database error: {{e}}\")\n")
                        updated_lines.append(f"{indent}    flash(\"An error occurred while processing your request. Please try again later.\", \"error\")\n")
                        updated_lines.append(f"{indent}    return redirect(url_for('main.index'))\n")
                        
                        i = end_j + 1  # Skip processed lines
                    else:
                        updated_lines.append(line)
                        i += 1
                
                # Write back if changes were made
                if updated_lines != lines:
                    with open(routes_file, 'w') as f:
                        f.writelines(updated_lines)
                    modified_files.append(routes_file)
                    print(f"Added try-except blocks to {routes_file}")
    
    return modified_files

def update_models_defaults():
    """Add safer default handling to models.py"""
    models_file = os.path.join('app', 'models.py')
    
    if os.path.exists(models_file):
        with open(models_file, 'r') as f:
            content = f.read()
        
        # Update BiasReport model
        updated_content = re.sub(
            r'(visualizations = db\.Column\(db\.JSON\))',
            r'visualizations = db.Column(db.JSON, default=lambda: "{}")',
            content
        )
        
        updated_content = re.sub(
            r'(explainability = db\.Column\(db\.JSON\))',
            r'explainability = db.Column(db.JSON, default=lambda: "{}")',
            updated_content
        )
        
        # Update BiasRecommendation model
        updated_content = re.sub(
            r'(action_items = db\.Column\(db\.JSON\))',
            r'action_items = db.Column(db.JSON, default=lambda: "[]")',
            updated_content
        )
        
        # Write back if changes were made
        if updated_content != content:
            with open(models_file, 'w') as f:
                f.write(updated_content)
            print(f"Updated models.py with safer defaults")
            return True
    
    return False

if __name__ == "__main__":
    print("--- Adding error handling to attribute access ---")
    modified_files = add_error_handling_to_routes()
    
    print("\n--- Adding try-except blocks to database operations ---")
    try_except_files = add_try_except_to_routes()
    
    print("\n--- Updating models with safer defaults ---")
    updated_models = update_models_defaults()
    
    if modified_files or try_except_files or updated_models:
        print("\nModified files:")
        for f in set(modified_files + try_except_files):
            print(f"- {f}")
        
        print("\nFinished adding error handling to routes.")
        print("Please restart your Flask application with 'python run.py' and test it again.") 