FROM ubuntu:latest
WORKDIR /app
RUN apt-get update && apt-get install -y \
	iproute2 \
	iputils-ping \
	procps \
	hostname \
	&& rm -rf /var/lib/apt/lists/*

COPY health_check.sh /app/health_check.sh
CMD ["bash","/app/health_check.sh"]

