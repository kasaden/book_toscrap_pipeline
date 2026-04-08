# Use Python image based on a Linux Image
FROM python:3.12-slim

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /pipeline

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and entrypoint
COPY app/ ./app/
COPY crontab.sh .
RUN sed -i 's/\r//' crontab.sh && chmod +x crontab.sh

# Data directory (overridden by volume in docker-compose)
RUN mkdir -p data

# Run the crontab
CMD ["./crontab.sh"]

# Run the crontab script avec interpéteur explicite (ici bash)
# CMD ["bash", "crontab.sh"]
