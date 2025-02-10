# Use an official Python runtime as a base image (Bookworm)
FROM python:3.9-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the application dependencies definition
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set environment variables for database connection (IMPORTANT!)
ENV MYSQL_HOST=192.168.40.13 
# Replace with your MySQL server's IP or hostname
ENV MYSQL_USER=quiz_user  
# Replace with your MySQL username
ENV MYSQL_PASSWORD=quiz@123 
# Replace with your MySQL password
ENV MYSQL_DATABASE=quiz_app 
# Replace with your database name

# Expose the port the app runs on (usually 5000 for Flask)
EXPOSE 443

# Define the command to run the application (using Flask's built-in development server)
CMD ["python", "app.py"]
