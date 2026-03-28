# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Non-root user for security (UID 1001 — must match k8s securityContext.runAsUser)
RUN addgroup --system appgroup \
 && adduser --system --uid 1001 --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from the builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

USER appuser

EXPOSE 8000

# Uvicorn: 1 worker per container (horizontal scaling is handled by k8s)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
