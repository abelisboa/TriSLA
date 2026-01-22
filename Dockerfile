FROM python:3.11-slim
RUN pip install flask
COPY traffic_exporter.py /traffic_exporter.py
CMD ["python", "/traffic_exporter.py"]
