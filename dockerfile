# Dockerfile for my elearning app
FROM python:3.12-slim

# Set up working directory
WORKDIR /app

#install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

#Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port 
EXPOSE 8080

# RUN Collectstatic during build
RUN python manage.py collectstatic --noinput

#Running the app with Gunicorn
CMD ["gunicorn", "elearning_platform.wsgi:application", "--bind", "0.0.0.0:8080"]





