FROM python:3.10.12-slim

WORKDIR /app

COPY docker/bot/requirements.txt .
RUN pip install -r requirements.txt

# CMD ["/usr/bin/supervisord","-c","/etc/supervisor/conf.d/supervisord.conf"]
# app command
CMD ["python", "-u", "bot.py"]