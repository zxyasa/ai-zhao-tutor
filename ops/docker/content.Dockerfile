FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy content service code
COPY . .

# Create output directory
RUN mkdir -p output

# Default command
CMD ["python", "generate_items.py"]
