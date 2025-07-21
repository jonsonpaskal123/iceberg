# نقشه راه پروژه عملی: خواندن از Elasticsearch و ذخیره در Iceberg با Nessie

این مستند، نقشه راه گام به گام برای ساخت یک پروژه کامل است که در آن داده‌ها از Elasticsearch خوانده شده و در یک جدول Apache Iceberg با استفاده از کاتالوگ Nessie ذخیره می‌شوند.

**پشته تکنولوژی (Technology Stack):**

*   **منبع داده:** Elasticsearch
*   **پردازش:** Apache Spark
*   **فرمت جدول:** Apache Iceberg
*   **کاتالوگ:** Nessie
*   **ذخیره‌سازی:** MinIO
*   **ارکستراسیون:** Docker Compose

---

## ساختار پروژه

```
/iceberg-nessie-project
|-- docker-compose.yml
|-- scripts/
|   `-- 01_elastic_to_iceberg.py
`-- roadmap.md
```

---

## مرحله ۱: ایجاد فایل Docker Compose

محتوای فایل `docker-compose.yml` را به شکل زیر ایجاد می‌کنیم. سرویس Spark طوری تنظیم می‌شود که همیشه در حال اجرا باقی بماند تا بتوانیم اسکریپت خود را در آن اجرا کنیم.

```yaml
version: '3'

services:
  elasticsearch:
    image: elasticsearch:8.11.1
    container_name: elasticsearch
    environment:
      - "discovery.type=single-node"
      - "xpack.security.enabled=false"
    ports:
      - "9200:9200"

  kibana:
    image: kibana:8.11.1
    container_name: kibana
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  nessie:
    image: projectnessie/nessie:latest
    container_name: nessie
    ports:
      - "19120:19120"

  minio:
    image: minio/minio:latest
    container_name: minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=password
    command: server /data --console-address ":9001"

  spark-runner:
    image: jupyter/pyspark-notebook:latest
    container_name: spark-runner
    depends_on:
      - nessie
      - minio
      - elasticsearch
    volumes:
      - ./scripts:/home/jovyan/work/scripts
    command: tail -f /dev/null
```

---

## مرحله ۲: بالا آوردن سرویس‌ها

با استفاده از دستور زیر، تمام سرویس‌ها را راه‌اندازی می‌کنیم.

```bash
docker-compose up -d
```

---

## مرحله ۳: درج داده در Elasticsearch

به آدرس `http://localhost:5601` بروید تا به Kibana دسترسی پیدا کنید. سپس به بخش **Dev Tools** رفته و دستورات زیر را برای ایجاد ایندکس و درج داده‌های نمونه اجرا کنید.

```bash
# ایجاد ایندکس با نگاشت (mapping) صحیح
PUT /app_logs
{
  "mappings": {
    "properties": {
      "ts": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" }
    }
  }
}

# درج دو رکورد نمونه
POST /app_logs/_doc
{ "ts": "2023-10-27T10:00:00Z", "level": "INFO", "message": "User logged in" }

POST /app_logs/_doc
{ "ts": "2023-10-27T10:05:00Z", "level": "WARNING", "message": "Disk space is running low" }
```

---

## مرحله ۴: ایجاد اسکریپت Spark

یک فایل پایتون در پوشه `scripts` به نام `01_elastic_to_iceberg.py` ایجاد کرده و کدهای زیر را در آن قرار می‌دهیم.

```python
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

```

---

## مرحله ۵: نحوه اجرا

1.  فایل `docker-compose.yml` و `roadmap.md` را در ریشه پروژه ایجاد کنید.
2.  پوشه `scripts` را بسازید و فایل `01_elastic_to_iceberg.py` را در آن قرار دهید.
3.  دستور `docker-compose up -d` را اجرا کنید تا تمام سرویس‌ها راه‌اندازی شوند.
4.  با استفاده از Kibana (`http://localhost:5601`) داده‌های اولیه را در Elasticsearch درج کنید.
5.  اسکریپت Spark را با دستور زیر اجرا کنید:
    ```bash
    docker exec spark-runner spark-submit \
      --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.75.0 \
      /home/jovyan/work/scripts/01_elastic_to_iceberg.py
    ```

```