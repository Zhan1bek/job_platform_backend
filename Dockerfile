
FROM python:3.11-slim


ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=job_platform.settings \
    PERSISTENT_DIR=/data


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN python manage.py collectstatic --noinput


CMD ["sh", "-c", "python manage.py migrate --noinput && uvicorn job_platform.asgi:application --host 0.0.0.0 --port 8000"]
