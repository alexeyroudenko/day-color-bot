FROM apache/airflow:2.10.2-python3.11

USER root
RUN apt update && apt install -y --no-install-recommends libgl1
RUN apt-get install -y gosu git

RUN echo "airflow:airflow" | chpasswd && adduser airflow sudo

WORKDIR /app
RUN chown -R airflow /app

USER airflow

RUN pip install pillow
RUN pip install git+https://github.com/alexeyroudenko/bing_image_downloader.git
RUN pip install scikit-learn
RUN pip install opencv-python-headless
RUN pip install matplotlib 
RUN pip install scikit-image
# COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
#RUN mkdir /app/data
#RUN mkdir /app/data/tmp
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# USER root