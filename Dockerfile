FROM apache/airflow:slim-latest-python3.13

USER root
RUN apt-get update && \
    apt-get -y install git && \
    apt-get clean
    
USER airflow 
RUN pip install pandas
