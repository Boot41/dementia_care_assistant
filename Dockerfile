# Backend Dockerfile

# Use official Python 3.12 image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY  requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY backend/ /app/

# Expose Django's default port
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
