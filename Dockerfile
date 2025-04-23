
# Use official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY . /app

# Expose port (Fly uses this)
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
