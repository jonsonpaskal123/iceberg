from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("Elastic-to-Iceberg") \
        .master("local[*]") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions") \
        .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.nessie.uri", "http://nessie:19120/api/v1") \
        .config("spark.sql.catalog.nessie.ref", "main") \
        .config("spark.sql.catalog.nessie.authentication.type", "NONE") \
        .config("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog") \
        .config("spark.sql.catalog.nessie.warehouse", "s3a://warehouse") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "password") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()

    print("Spark session created successfully.")

    # خواندن داده از Elasticsearch
    print("Reading data from Elasticsearch...")
    elastic_df = spark.read.format("org.elasticsearch.spark.sql") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "app_logs") \
        .load()
    print("Data read from Elasticsearch:")
    elastic_df.show()

    # ایجاد جدول آیسبرگ
    print("Creating Iceberg table...")
    spark.sql("""
        CREATE TABLE IF NOT EXISTS nessie.logs (
          ts TIMESTAMP,
          level STRING,
          message STRING
        )
        PARTITIONED BY (level)
    """)
    print("Iceberg table 'nessie.logs' created.")

    # نوشتن داده‌ها در جدول آیسبرگ
    print("Writing data to Iceberg table...")
    elastic_df.write.format("iceberg").mode("append").save("nessie.logs")
    print("Data written to Iceberg successfully.")

    # بررسی داده‌های نوشته شده
    print("Verifying data in Iceberg table:")
    iceberg_df = spark.table("nessie.logs")
    iceberg_df.show()

    spark.stop()

if __name__ == "__main__":
    main()