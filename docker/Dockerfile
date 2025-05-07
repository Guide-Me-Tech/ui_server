# Use the official Python image
FROM python:3.12

# Set environment to help with performance and security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Add a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Adjust permissions for non-root
RUN chown -R appuser:appgroup /app
USER appuser

#EXPOSE 8000

# Healthcheck to detect issues early
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["fastapi", "run", "src/server.py"]
