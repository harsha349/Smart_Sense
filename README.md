# SmartPantry Agent (NutriScan AI) - Agentified Project

This repository contains a Cloud Run–ready, agentified version of SmartPantry (NutriScan AI).
It includes:
- a Flask backend (Cloud Run) that orchestrates multiple sub-agents (vision, planner, nutrition, recipe, health, grocery)
- a small local nutrition DB (nutrition_db.json)
- a simple frontend (index.html + app.js)
- Dockerfile, requirements.txt, and Cloud Build config (cloudbuild.yaml)
- agent_orchestrator.py which coordinates all agents

## Quick start (Cloud Shell)
1. Upload this project to GitHub or copy to Cloud Shell.
2. Set your GCP project and enable APIs:
   ```
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com storage.googleapis.com firestore.googleapis.com
   ```
3. Create a GCS bucket and Firestore DB, and a service account with required roles.
4. Build & deploy:
   ```
   cd backend
   gcloud builds submit --tag asia-south1-docker.pkg.dev/$PROJECT_ID/fridgevision-repo/fridgevision:latest
   gcloud run deploy fridgevision --image asia-south1-docker.pkg.dev/$PROJECT_ID/fridgevision-repo/fridgevision:latest --region asia-south1 --platform managed --allow-unauthenticated --set-env-vars BUCKET_NAME=YOUR_BUCKET,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,REGION=asia-south1
   ```
5. Call the API:
   ```
   curl -X POST -F "image=@fridge.jpg" -F "diet=high-protein" https://YOUR_CLOUD_RUN_URL/api/analyze
   ```
