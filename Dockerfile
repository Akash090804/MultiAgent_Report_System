FROM python:3.11-slim

WORKDIR /app
# For reportlab dependencies 
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY my_agent /app/my_agent/
COPY Web_app /app/Web_app/

RUN mkdir -p /app/Web_app/outputs && chmod 777 /app/Web_app/outputs

ENV PYTHONPATH=/app:/app/my_agent:/app/Web_app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app/Web_app

EXPOSE 8000

CMD ["uvicorn","backend.api:app","--host","0.0.0.0","--port","8000"]
 