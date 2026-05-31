FROM python:3.10-slim-buster

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install explicit, hardened dependency matrix
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.2.2

# Copy code asset into isolated container workspace
COPY calibrate.py /app/calibrate.py

# Strip root privileges and run as a secure non-root TEE user
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["python", "/app/calibrate.py"]
