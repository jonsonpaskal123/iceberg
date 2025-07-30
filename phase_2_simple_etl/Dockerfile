FROM apache/spark:3.5.1-python3

USER root

# Create .ivy2 directory and set permissions for spark user
RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark/.ivy2

# Install boto3 for MinIO access
RUN pip install boto3

USER spark
