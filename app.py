from flask import Flask, jsonify

# Create a minimal Flask app as a final fallback
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({
        "status": "online",
        "message": "This is the root-level fallback app. The main application structure may be incompatible with Vercel."
    })

# For local testing
if __name__ == '__main__':
    app.run(debug=True) 