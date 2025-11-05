FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && python -m spacy download pt_core_news_sm
COPY . .
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8081"]