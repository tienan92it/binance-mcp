# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container first
# This leverages Docker's build cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir keeps the image size down
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes the binance_mcp_server directory, run_server.py, etc.
COPY . .

# Optional: Environment variables for API keys (if needed for private endpoints)
# These can also be set during 'docker run' using the -e flag.
# ENV BINANCE_API_KEY="your_api_key"
# ENV BINANCE_API_SECRET="your_secret_key"

# Command to run the application when the container launches
# This runs the MCP server listening via STDIO by default.
# To run with SSE, you would need to adjust the CMD or override it during 'docker run'.
CMD ["python", "run_server.py"] 