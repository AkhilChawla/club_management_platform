FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    "Django>=4.2,<5.0" \
    "djangorestframework>=3.14,<4.0" \
    "pika>=1.3.0" \
    "requests>=2.31"

# Copy service code
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port
EXPOSE 8000

# Start the service
CMD ["/entrypoint.sh"]
