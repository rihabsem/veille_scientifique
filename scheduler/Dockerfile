FROM python:3.12-slim

RUN apt-get update && apt-get install -y cron curl

WORKDIR /app

COPY . .

RUN pip install requests

COPY crontab /etc/cron.d/scheduler
RUN chmod 0644 /etc/cron.d/scheduler
RUN crontab /etc/cron.d/scheduler

CMD ["bash", "-c", "crontab /etc/cron.d/scheduler && cron -f"]