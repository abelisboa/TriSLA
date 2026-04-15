# TriSLA Traffic Exporter — v3.10.0
# Base reprodutível para baseline científico (PROMPT_S52)
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    METRICS_PORT=9105

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 9105

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9105"]
