from flask import Flask, jsonify

# Create a fallback app in case the main app fails to load
fallback_app = Flask(__name__)

@fallback_app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "message": "Fallback app is running. Main app initialization may have failed."
    })

@fallback_app.route('/<path:path>')
def catch_all(path):
    return jsonify({
        "status": "error",
        "message": "Fallback app is handling this request. The main application may have failed to initialize."
    })

try:
    # Try to import the main app
    from app import create_app
    app = create_app()
except Exception as e:
    # If main app fails, use the fallback app
    import traceback
    print(f"Error initializing main app: {e}")
    print(traceback.format_exc())
    app = fallback_app 