FROM python:3.12-slim

ARG http_proxy
ARG https_proxy

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY monitoring_app.py .

EXPOSE 8502

CMD ["streamlit", "run", "monitoring_app.py", \
     "--server.port=8502", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]