FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy frontend files
COPY . .

# Expose port
EXPOSE 3000

# Serve static files using Python's built-in server
CMD ["python", "-m", "http.server", "3000"]
