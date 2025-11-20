# FridgeVision Pro
FridgeVision Pro - upload a fridge photo → detect ingredients → generate recipes + nutrition + health insights.

## What is included
- Backend (Flask) with Vertex AI integration (vision + Gemini)
- Simple frontend (HTML + JS)
- Dockerfile for Cloud Run
- prompts.py, utils.py, and requirements.txt

## Quick start (local / cloud)
1. Set up a GCP project and enable APIs (run.googleapis.com, aiplatform.googleapis.com, storage.googleapis.com, firestore.googleapis.com, artifactregistry.googleapis.com, cloudbuild.googleapis.com).
2. Create a Cloud Storage bucket and Firestore database.
3. Create a service account and grant roles: roles/aiplatform.user, roles/storage.objectAdmin, roles/datastore.user.
4. Set environment variables before deploying to Cloud Run:
   - BUCKET_NAME
   - GOOGLE_CLOUD_PROJECT
   - REGION (asia-south1 recommended)
5. Build & push container:
   ```
   gcloud builds submit --tag asia-south1-docker.pkg.dev/$PROJECT_ID/fridgevision-repo/fridgevision:latest backend/
   ```
6. Deploy to Cloud Run:
   ```
   gcloud run deploy fridgevision              --image asia-south1-docker.pkg.dev/$PROJECT_ID/fridgevision-repo/fridgevision:latest              --region asia-south1              --platform managed              --service-account $SA_EMAIL              --allow-unauthenticated              --set-env-vars BUCKET_NAME=$BUCKET,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,REGION=asia-south1
   ```

## Notes
- This template uses the `vertexai` python package. When running on Cloud Run, attach a service account with the needed permissions so no JSON key is required.
- The Vision + Gemini usage in the sample is simplified for hackathon speed; you may need to adapt calls depending on the installed SDK versions or use REST calls.
