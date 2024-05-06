# Use the official Python image as a base image
FROM python:3.9

# Set environment variables
ENV FLASK_ENV=production
ENV FLASK_APP=my_app.py

# Copy the application files to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "my_app.py"]
