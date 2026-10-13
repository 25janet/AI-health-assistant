FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    procps \
    hostname \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY monitoring/ /app/monitoring
COPY scripts/ /app/scripts
COPY app/ /app/app
COPY requirements.txt /app/requirements.txt

RUN chmod +x /app/monitoring/health_check.sh \
        /app/scripts/*.sh

RUN pip3 install --break-system-packages -r requirements.txt
RUN mkdir -p /app/data/raw \
        /app/data/processed 

CMD ["bash", "-c", "bash /app/monitoring/health_check.sh 2>&1 | tee -a /app/data/raw/health.log"]
