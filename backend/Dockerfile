FROM python:3.11.8-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies, including poppler-utils
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
        poppler-utils \
        build-essential \
        curl \
        gcc \
        libffi-dev \
        libssl-dev \
        ca-certificates && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Set default command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
