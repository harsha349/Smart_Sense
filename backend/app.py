import os
from flask import Flask, request, jsonify, send_from_directory
from google.cloud import storage, firestore
# vertexai package imports
try:
    from vertexai import client as vertex_client
    from vertexai import language as vertex_language
    from vertexai import Vision
except Exception:
    # If vertexai package isn't available in your environment, you'll need to adapt to use google-cloud-aiplatform or REST.
    vertex_client = None
    vertex_language = None
    Vision = None

from prompts import BASE_RECIPE_PROMPT
from utils import read_image_bytes

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# Environment / GCP settings
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
BUCKET = os.environ.get("BUCKET_NAME")
REGION = os.environ.get("REGION", "asia-south1")

# initialize Firestore and Storage
db = firestore.Client() if PROJECT else None
storage_client = storage.Client() if PROJECT else None

if vertex_client:
    vertex_client.init(project=PROJECT, location=REGION)

TEXT_MODEL_NAME = "gemini-1.5-flash"
VISION_MODEL_NAME = "vision-bison"  # adjust if needed

@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "missing image file"}), 400

    img_bytes = read_image_bytes(file)

    # 1) Upload image to Cloud Storage
    blob_name = f"uploads/{file.filename}"
    if storage_client:
        bucket = storage_client.bucket(BUCKET)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(img_bytes, content_type=file.content_type)
        image_gs_uri = f"gs://{BUCKET}/{blob_name}"
    else:
        image_gs_uri = file.filename

    # 2) Try Vision detection: prefer vertex Vision, else fallback to text LLM asking to list items
    ingredients = ""
    try:
        if Vision:
            vision = Vision.VisionClient()
            resp = vision.predict_image(content=img_bytes)
            labels = [l.display_name for l in resp.labels]
            ingredients = ", ".join(labels)
        else:
            # fallback: ask text model to list ingredients from the image URI
            if vertex_language:
                language_model = vertex_language.TextGenerationModel.from_pretrained(TEXT_MODEL_NAME)
                prompt = f"Look at the image at {image_gs_uri} and list all visible food items as a comma separated list."
                gen = language_model.predict(prompt)
                ingredients = gen.text
            else:
                ingredients = "eggs, tomato, spinach"  # placeholder
    except Exception as e:
        # if anything fails, simple placeholder
        ingredients = "eggs, tomato, spinach"

    # 3) Prepare recipe prompt and append diet
    final_prompt = BASE_RECIPE_PROMPT.format(ingredients=ingredients)
    diet = request.form.get("diet")
    if diet:
        final_prompt += f"\nUser diet preference: {diet}\n"

    # 4) Call Gemini/Text model for recipes & nutrition
    result_text = ""
    try:
        if vertex_language:
            language_model = vertex_language.TextGenerationModel.from_pretrained(TEXT_MODEL_NAME)
            recipe_gen = language_model.predict(final_prompt, max_output_tokens=1500)
            result_text = recipe_gen.text
        else:
            result_text = "Sample recipe output: Omelette with tomatoes and spinach..."
    except Exception as e:
        result_text = "Failed to generate recipe: " + str(e)

    # 5) Persist record in Firestore (if available)
    user_id = request.form.get("user_id", "anonymous")
    if db:
        doc_ref = db.collection("scans").document()
        doc_ref.set({
            "user_id": user_id,
            "image_uri": image_gs_uri,
            "ingredients": ingredients,
            "recipes_text": result_text,
        })

    return jsonify({
        "image_uri": image_gs_uri,
        "ingredients": ingredients,
        "recipes": result_text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
