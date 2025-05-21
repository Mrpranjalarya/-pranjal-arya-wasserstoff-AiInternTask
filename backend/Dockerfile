# FROM python:3.11.8-slim-bookworm
FROM python:3.11.8-slim-bookworm

# Update system packages to address vulnerabilities
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install --no-install-recommends -y ca-certificates && \
	apt-get autoremove -y && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*
