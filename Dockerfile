FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code

# Run as a non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Install dependencies first so Docker caches this layer
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

USER app

EXPOSE 8000

# python:slim has no curl, so use Python for the container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
