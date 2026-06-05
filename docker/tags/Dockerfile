FROM python:3.10.12-slim

# set a directory for the app
WORKDIR /app

# copy all the files to the container
# COPY . .
COPY docker/tags/requirements.txt .

RUN pip install -r requirements.txt

# app command
CMD ["python", "-u", "test.py"]