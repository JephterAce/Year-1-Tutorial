FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY frontend/ ./frontend/
COPY admin/ ./admin/
RUN useradd --system --uid 10001 learnwise && chown -R learnwise:learnwise /app
USER learnwise
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
CMD ["gunicorn","--bind=0.0.0.0:8000","--workers=2","--threads=4","--timeout=30","app:app"]
