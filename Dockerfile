FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir sympy==1.12

COPY ocean_router.py /app/ocean_router.py
RUN chmod +x /app/ocean_router.py

USER 1000

ENTRYPOINT ["python3", "/app/ocean_router.py"]
