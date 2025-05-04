from flask import Flask, jsonify, render_template_string
import os

# Create a simplified version of your app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Routes
@app.route('/')
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EthicAI - Simplified Version</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #333; }
                .alert { padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>EthicAI Platform</h1>
                <div class="alert">
                    <p>This is a simplified version of the EthicAI application running on Vercel.</p>
                    <p>The full version may require additional configuration to run in this environment.</p>
                </div>
                <h2>Main Features:</h2>
                <ul>
                    <li>Learning Hub</li>
                    <li>Bias Analyzer</li>
                    <li>Governance Framework</li>
                    <li>Virtual Assistant</li>
                </ul>
                <p>Status: Online in simplified mode</p>
            </div>
        </body>
        </html>
    """)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mode": "simplified"})

@app.route('/api/info')
def api_info():
    return jsonify({
        "app": "EthicAI",
        "version": "simplified",
        "environment": "Vercel",
        "status": "online"
    })

@app.route('/<path:path>')
def catch_all(path):
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Not Found</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; padding-top: 50px; }
                h1 { color: #333; }
                .alert { padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; margin-bottom: 20px; }
                a { color: #007bff; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Page Not Found</h1>
                <div class="alert">
                    <p>The page you requested could not be found.</p>
                </div>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
        </html>
    """), 404 