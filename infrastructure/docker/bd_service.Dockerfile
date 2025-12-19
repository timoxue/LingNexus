FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ ./config/
COPY shared/ ./shared/
COPY core_agents/bd_service/ ./core_agents/bd_service/

ENV PYTHONPATH=/app

CMD ["uvicorn", "core_agents.bd_service.api:app", "--host", "0.0.0.0", "--port", "8002"]
