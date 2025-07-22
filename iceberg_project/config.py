
from pyspark.sql import SparkSession

def get_spark_session():
    """
    Initializes and returns a Spark session with all the necessary configurations
    for Iceberg, Nessie, and MinIO.
    """
    return SparkSession.builder         .appName("Elastic-to-Iceberg")         .master("local[*]")         .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions")         .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")         .config("spark.sql.catalog.nessie.uri", "http://nessie:19120/api/v1")         .config("spark.sql.catalog.nessie.ref", "main")         .config("spark.sql.catalog.nessie.authentication.type", "NONE")         .config("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")         .config("spark.sql.catalog.nessie.warehouse", "s3a://warehouse")         .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")         .config("spark.hadoop.fs.s3a.access.key", "admin")         .config("spark.hadoop.fs.s3a.secret.key", "password")         .config("spark.hadoop.fs.s3a.path.style.access", "true")         .getOrCreate()
