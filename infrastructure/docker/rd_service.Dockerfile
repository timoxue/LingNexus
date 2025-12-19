FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ ./config/
COPY shared/ ./shared/
COPY core_agents/rd_service/ ./core_agents/rd_service/

ENV PYTHONPATH=/app

CMD ["uvicorn", "core_agents.rd_service.api:app", "--host", "0.0.0.0", "--port", "8003"]
