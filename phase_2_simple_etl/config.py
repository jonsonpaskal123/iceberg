from pyspark.sql import SparkSession

def get_spark_session():
    """
    Initializes and returns a Spark session with configurations for MinIO.
    """
    return SparkSession.builder         .appName("Elastic-to-MinIO")         .master("local[*]")         .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")         .config("spark.hadoop.fs.s3a.access.key", "admin")         .config("spark.hadoop.fs.s3a.secret.key", "password")         .config("spark.hadoop.fs.s3a.path.style.access", "true")         .getOrCreate()
