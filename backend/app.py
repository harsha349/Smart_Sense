import os
from flask import Flask, request, jsonify, send_from_directory
from utils import read_image_bytes
try:
    from agent_orchestrator import orchestrate
except Exception as e:
    orchestrate = None
    print("agent_orchestrator import failed:", e)

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    file = request.files.get('image')
    if not file:
        return jsonify({'error':'missing image file'}), 400
    img_bytes = read_image_bytes(file)
    diet = request.form.get('diet','none')
    user_id = request.form.get('user_id','anonymous')
    if orchestrate:
        final = orchestrate(img_bytes, user_diet=diet, user_id=user_id)
        return jsonify(final)
    else:
        return jsonify({'error':'orchestrator not available'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',8080)))
