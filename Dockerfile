FROM python:3.10.12

# install system wide dependencies
# RUN apt-get -yqq update
# RUN apt-get -yqq install ffmpeg

# set a directory for the app
WORKDIR /app

# copy all the files to the container
COPY . .
RUN mkdir ./input_media ./output_media

RUN apt update && apt install -y --no-install-recommends nginx-extras libfontconfig1 libxrender1 libgl1-mesa-glx cron supervisor 
# install app-specific dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-telegram-bot[job-queue]
RUN apt-get install libgl1

# Configure cron jobs and ensure crontab-file permissions
RUN chmod 0644 /etc/cron.d/*

# COPY nginx.conf /etc/nginx/nginx.conf

# ADD crontab.txt /crontab.txt
# RUN /usr/bin/crontab /crontab.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# CMD ["/usr/bin/supervisord","-c","/etc/supervisor/conf.d/supervisord.conf"]

# app command
CMD ["python", "-u", "./main.py"]