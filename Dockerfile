FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_MODULE=app.main:app \
    DATABASE_URL=sqlite:////data/app.db

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN useradd --create-home --uid 1000 appuser \
    && mkdir /data \
    && chown -R appuser:appuser /app /data
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn $APP_MODULE --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]