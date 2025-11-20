# import os
# import logging
# from flask import Flask, request, jsonify, send_from_directory
# import sys

# # Add backend/ to path for utils and orchestrator
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from utils import read_image_bytes

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Try to import orchestrator
# try:
#     from agent_orchestrator import orchestrate
# except Exception as e:
#     orchestrate = None
#     logging.warning(f"agent_orchestrator import failed: {e}")

# # Set frontend path relative to Smart_Sense root
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='/')

# # Root route serves frontend index.html
# @app.route('/')
# def index():
#     return send_from_directory(app.static_folder, 'index.html')

# # API endpoint
# @app.route('/api/analyze', methods=['POST'])
# def analyze():
#     file = request.files.get('image')
#     if not file:
#         return jsonify({'error': 'missing image file'}), 400

#     img_bytes = read_image_bytes(file)
#     diet = request.form.get('diet', 'none')
#     user_id = request.form.get('user_id', 'anonymous')

#     if orchestrate:
#         try:
#             final = orchestrate(img_bytes, user_diet=diet, user_id=user_id)
#             return jsonify(final)
#         except Exception as e:
#             logging.error(f"Error during orchestrate: {e}")
#             return jsonify({'error': 'internal processing error'}), 500
#     else:
#         logging.error("Orchestrator not available")
#         return jsonify({'error': 'orchestrator not available'}), 500

# # Entry point
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 8080))
#     logging.info(f"Starting Flask server on 0.0.0.0:{port}")
#     app.run(host='0.0.0.0', port=port)

#...............................................
import logging
import sys, os
from flask import Flask, request, jsonify, send_from_directory

# Add backend folder to path
sys.path.append(os.path.dirname(__file__))

# Import utils
from .utils import read_image_bytes

# Try to import orchestrator
try:
    from .agent_orchestrator import orchestrate
except Exception as e:
    orchestrate = None
    logging.warning(f"agent_orchestrator import failed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Flask app pointing to frontend folder
app = Flask(__name__, static_folder='../frontend', static_url_path='/')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'missing image file'}), 400

    img_bytes = read_image_bytes(file)
    diet = request.form.get('diet', 'none')
    user_id = request.form.get('user_id', 'anonymous')

    if orchestrate:
        try:
            final = orchestrate(img_bytes, user_diet=diet, user_id=user_id)
            return jsonify(final)
        except Exception as e:
            logging.error(f"Error during orchestrate: {e}")
            return jsonify({'error': 'internal processing error'}), 500
    else:
        logging.error("Orchestrator not available")
        return jsonify({'error': 'orchestrator not available'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting Flask server on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)