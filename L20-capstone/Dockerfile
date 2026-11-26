# Base: python:3.12-slim. (In the recording sandbox Docker Hub was blocked, so the same file was built with
#   --build-arg BASE=<a local Ubuntu 24.04 + Python 3.12 image>; nothing else changes.)
ARG BASE=python:3.12-slim
FROM ${BASE}
WORKDIR /srv
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt
COPY app ./app
ENV OLLAMA_URL=http://ollama:11434 MODEL=qwen3.5:4b TRACES=/srv/traces/traces.jsonl
RUN mkdir -p /srv/traces
EXPOSE 8000
HEALTHCHECK CMD python3 -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
