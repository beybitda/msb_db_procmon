FROM python:3.12-slim

ARG http_proxy
ARG https_proxy

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app.py .
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/

EXPOSE 8502

CMD ["streamlit", "run", "app.py", \
     "--server.port=8502", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
