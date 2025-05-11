FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=job_platform.settings \
    PERSISTENT_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic
RUN python job_platform/manage.py collectstatic --noinput

# запускаем Gunicorn из папки, где виден job_platform/
WORKDIR /app/job_platform
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "job_platform.wsgi:application"]
