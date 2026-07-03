FROM python:3.12-slim

WORKDIR /app

# System deps for hermes-agent + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install hermes-agent
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

COPY . .

# Ensure hermes is on PATH
ENV PATH="/root/.local/bin:${PATH}"
ENV HERMES_HOME=/home/ec2-user/.hermes

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
