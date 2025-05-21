FROM python:3.11-slim-bookworm@sha256:0e7b2a5e3e2e3b7c6b8e6e8e2b8e2b8e2b8e2b8e2b8e2b8e2b8e2b8e2b8e2b8e2b

# Install security updates and remove unnecessary packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]