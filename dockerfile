FROM python:3.9-alpine

COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Use proper JSON format for CMD to handle signals correctly
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]