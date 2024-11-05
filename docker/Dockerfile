# Use the official Python image as a base
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .
# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "src/server.py"]
