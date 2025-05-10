# 1) базовый образ
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 2) зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) код
COPY . .

# 4) сбор статики
RUN python manage.py collectstatic --noinput

# 5) директория для постоянных данных (Render подмонтирует /data)
ENV PERSISTENT_DIR=/data

CMD ["uvicorn", "job_platform.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
