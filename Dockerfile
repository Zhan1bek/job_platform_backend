FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=job_platform.settings \
    PERSISTENT_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python job_platform/manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "job_platform.wsgi:application"]
