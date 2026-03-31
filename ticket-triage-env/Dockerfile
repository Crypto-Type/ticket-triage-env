FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir fastapi uvicorn pydantic pyyaml openai requests

# Copy all project files
COPY . .

# Expose the port HF Spaces expects
EXPOSE 7860

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
