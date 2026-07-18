FROM python:3.11-slim

WORKDIR /app

COPY apps/ran-ue-upf-proxy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/ran-ue-upf-proxy/exporter.py .

EXPOSE 9102

CMD ["gunicorn", "--bind", "0.0.0.0:9102", "--workers", "2", "--threads", "4", "exporter:app"]

