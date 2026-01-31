FROM python:3.11-slim

WORKDIR /app

COPY ../requirements_offline.txt .
RUN pip install --no-cache-dir \
  -r requirements_offline.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --extra-index-url https://download.pytorch.org/whl/cu121

CMD ["python", "ai_voice_service_offline.py"]