FROM python:3.11-slim

LABEL description="SDN Controller for network device automation via NETCONF"

RUN apt-get update && apt-get install -y --no-install-recommends gcc libxml2-dev libxslt-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY inventory/ ./inventory/
COPY run.py .

EXPOSE 5000

CMD ["python", "run.py"]
