FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY plc_fleet/ ./plc_fleet/

EXPOSE 502

ENTRYPOINT ["python", "-m", "plc_fleet.main"]