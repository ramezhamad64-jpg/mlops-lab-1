FROM python:3.11-slim

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=600 --retries 20 streamlit==1.39.0 requests==2.32.3

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
