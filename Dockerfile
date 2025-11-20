# # Base image
# FROM python:3.10-slim

# # Set working directory
# WORKDIR /app

# # Copy requirements and install
# COPY backend/requirements.txt .
# RUN pip install --upgrade pip \
#     && pip install --no-cache-dir -r requirements.txt

# # Copy backend and frontend code
# COPY backend/ ./backend
# COPY frontend/ ./frontend

# # Set environment
# ENV PORT=8080
# EXPOSE 8080

# # Start server using Gunicorn
# CMD ["gunicorn", "-b", "0.0.0.0:8080", "backend.app:app"]

#.......................................working above

# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend and frontend
COPY backend/ backend/
COPY frontend/ frontend/

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Start the app
CMD ["gunicorn", "backend.app:app", "--bind", "0.0.0.0:8080", "--workers", "2"]