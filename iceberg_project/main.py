import boto3
from botocore.exceptions import ClientError
from config import get_spark_session
from elastic_reader import read_from_elastic
from iceberg_writer import create_iceberg_table, write_to_iceberg, verify_iceberg_data

def ensure_minio_bucket_exists(bucket_name: str):
    """
    Checks if a MinIO bucket exists and creates it if it does not.
    """
    print(f"Checking for MinIO bucket: {bucket_name}")
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='admin',
        aws_secret_access_key='password'
    )
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{bucket_name}' does not exist. Creating it...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print("An error occurred while checking the bucket:")
            raise

def main():
    """
    Main ETL pipeline to move data from Elasticsearch to Iceberg.
    """
    spark = None
    try:
        # 0. Ensure MinIO bucket exists
        ensure_minio_bucket_exists("warehouse")

        # 1. Get Spark Session
        spark = get_spark_session()
        print("Spark session created successfully.")

        # 2. Read data from Elasticsearch
        elastic_df = read_from_elastic(spark, "persons")

        # 3. Define Iceberg table properties
        table_name = "nessie.persons"
        schema = "person_id INT, first_name STRING, last_name STRING, email STRING, code_melli STRING, city STRING"
        partition_by = "city"

        # 4. Create Iceberg table
        create_iceberg_table(spark, table_name, schema, partition_by)

        # 5. Write data to Iceberg
        write_to_iceberg(elastic_df, table_name)

        # 6. Verify the data
        verify_iceberg_data(spark, table_name)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if spark:
            print("Stopping Spark session.")
            spark.stop()

if __name__ == "__main__":
    main()