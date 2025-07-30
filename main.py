import boto3
from botocore.exceptions import ClientError
from pyspark.sql import SparkSession, DataFrame
from config import get_spark_session

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

def read_from_elastic(spark: SparkSession, es_resource: str) -> DataFrame:
    """
    Reads data from a specified Elasticsearch resource.
    """
    print(f"Reading data from Elasticsearch resource: {es_resource}...")
    df = spark.read.format("org.elasticsearch.spark.sql") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", es_resource) \
        .load()
    print("Data read successfully.")
    df.show()
    return df

def write_to_minio(df: DataFrame, bucket_name: str, path: str):
    """
    Writes a DataFrame to MinIO in Parquet format.
    """
    print(f"Writing data to MinIO bucket '{bucket_name}' at path '{path}'...")
    df.write.format("parquet").mode("overwrite").save(f"s3a://{bucket_name}/{path}")
    print("Data written successfully.")

def main():
    """
    Main ETL pipeline to move data from Elasticsearch to MinIO.
    """
    spark = None
    try:
        # 1. Define constants
        es_index = "persons"
        minio_bucket = "phase-2-warehouse"
        output_path = "persons_data"

        # 2. Ensure MinIO bucket exists
        ensure_minio_bucket_exists(minio_bucket)

        # 3. Get Spark Session
        spark = get_spark_session()
        print("Spark session created successfully.")

        # 4. Read data from Elasticsearch
        elastic_df = read_from_elastic(spark, es_index)

        # 5. Write data to MinIO
        write_to_minio(elastic_df, minio_bucket, output_path)

        print("ETL process completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if spark:
            print("Stopping Spark session.")
            spark.stop()

if __name__ == "__main__":
    main()
