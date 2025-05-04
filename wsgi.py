from app import create_app

app = create_app()

# Handler for Vercel serverless environment
def handler(request, **kwargs):
    return app(request.environ, request.start_response) 