# Use the official Python image as the base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask app's port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
