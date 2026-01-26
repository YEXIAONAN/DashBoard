FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "test_main.py", "--host", "0.0.0.0", "--port", "8020"]