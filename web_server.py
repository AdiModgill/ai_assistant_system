# web_server.py
# Simple Flask development server to preview the AI Assistant web UI.
# Run with:  python web_server.py
# Then open: http://localhost:5000
#
# NOTE: This uses Flask's built-in development server which is NOT suitable
# for production.  For production deployments use a proper WSGI server such
# as Gunicorn:  gunicorn web_server:app

import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR  = os.path.join(BASE_DIR, 'web')

app = Flask(__name__, static_folder=WEB_DIR)


@app.route('/')
def index():
    return send_from_directory(WEB_DIR, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(WEB_DIR, filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'AI Assistant UI running at http://localhost:{port}')
    app.run(debug=False, port=port)
