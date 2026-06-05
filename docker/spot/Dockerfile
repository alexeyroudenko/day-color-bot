FROM python:3.10.12

# set a directory for the app
WORKDIR /app

COPY docker/spot/requirements.txt .

RUN apt update && apt install -y --no-install-recommends libgl1

RUN pip install Flask
RUN pip install redis
RUN pip install flask-socketio

RUN pip install -r requirements.txt

# app command
CMD ["python", "-u", "spot.py"]