FROM bitnami/spark:3.5.1

USER root
RUN pip install boto3

USER 1001

COPY main.py /opt/bitnami/spark/work-dir/main.py
COPY config.py /opt/bitnami/spark/work-dir/config.py
