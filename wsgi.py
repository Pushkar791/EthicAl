import sys
import traceback
import json
import os

try:
    from app import create_app
    app = create_app()

    # Handler for Vercel serverless environment
    def handler(request, **kwargs):
        try:
            # Logging request info for debugging
            print(f"Request path: {request.get('path', 'unknown')}")
            print(f"Request method: {request.get('method', 'unknown')}")
            
            # Return application response
            return app(request.environ, request.start_response)
        except Exception as e:
            # Log any errors that occur during request handling
            error_details = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "python_version": sys.version,
                "environment": dict(os.environ)
            }
            print(f"Error during request handling: {json.dumps(error_details)}")
            
            # Return a 500 error response
            response_body = json.dumps({"error": "Internal Server Error", "details": str(e)}).encode('utf-8')
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'application/json')]
            request.start_response(status, headers)
            return [response_body]
except Exception as e:
    # Log any errors that occur during application initialization
    print(f"Error initializing application: {e}")
    print(traceback.format_exc())
    
    # Define a fallback handler
    def handler(request, **kwargs):
        response_body = json.dumps({
            "error": "Application Initialization Failed",
            "details": str(e),
            "traceback": traceback.format_exc(),
            "python_version": sys.version
        }).encode('utf-8')
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json')]
        request.start_response(status, headers)
        return [response_body] 