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
|-- notebooks/
|   `-- 01-elastic-to-iceberg.ipynb
`-- roadmap.md
```

---

## مرحله ۱: راه‌اندازی زیرساخت با Docker Compose

محتوای فایل `docker-compose.yml` را به شکل زیر ایجاد می‌کنیم. این فایل سرویس‌های Elasticsearch و Kibana را نیز به پشته ما اضافه می‌کند.

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

  spark-iceberg-nessie:
    image: tabulario/spark-iceberg
    container_name: spark-iceberg-nessie
    depends_on:
      - nessie
      - minio
      - elasticsearch
    volumes:
      - ./notebooks:/home/iceberg/notebooks
    ports:
      - "8888:8888"
      - "4040:4040"
    environment:
      - SPARK_HOME=/opt/spark
      - SPARK_MASTER_HOST=spark-iceberg-nessie
    command: >
      /opt/spark/bin/pyspark
      --master local[*]
      --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3
      --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions
      --conf spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog
      --conf spark.sql.catalog.nessie.uri=http://nessie:19120/api/v1
      --conf spark.sql.catalog.nessie.ref=main
      --conf spark.sql.catalog.nessie.authentication.type=NONE
      --conf spark.sql.catalog.nessie.catalog-impl=org.apache.iceberg.nessie.NessieCatalog
      --conf spark.sql.catalog.nessie.warehouse=s3a://warehouse
      --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000
      --conf spark.hadoop.fs.s3a.access.key=admin
      --conf spark.hadoop.fs.s3a.secret.key=password
      --conf spark.hadoop.fs.s3a.path.style.access=true
      --conf spark.driver.memory=2g
```

---

## مرحله ۲: ایجاد و اجرای نوت‌بوک Spark

یک نوت‌بوک جدید در پوشه `notebooks` به نام `01-elastic-to-iceberg.ipynb` ایجاد کرده و کدهای زیر را در سلول‌های جداگانه اجرا می‌کنیم.

### الف) درج داده در Elasticsearch

ابتدا با استفاده از Kibana (در آدرس `http://localhost:5601`) یا دستورات cURL، یک ایندکس و چند داده نمونه در Elasticsearch ایجاد می‌کنیم.

```bash
# In Kibana Dev Tools or via cURL
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

POST /app_logs/_doc
{ "ts": "2023-10-27T10:00:00Z", "level": "INFO", "message": "User logged in" }

POST /app_logs/_doc
{ "ts": "2023-10-27T10:05:00Z", "level": "WARNING", "message": "Disk space is running low" }
```

### ب) خواندن داده از Elasticsearch در Spark

حالا در نوت‌بوک Spark، داده‌ها را از ایندکس `app_logs` می‌خوانیم.

```python
# In a PySpark cell

elastic_df = spark.read.format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.resource", "app_logs") \
    .load()

elastic_df.show()
```

### ج) ایجاد و نوشتن در جدول آیسبرگ

داده‌های خوانده شده را در یک جدول آیسبرگ که توسط Nessie مدیریت می‌شود، می‌نویسیم.

```sql
-- Create the Iceberg table
CREATE TABLE nessie.logs (
  ts TIMESTAMP,
  level STRING,
  message STRING
)
PARTITIONED BY (level);
```

```python
# Write the DataFrame to the Iceberg table
elastic_df.write.format("iceberg").mode("append").save("nessie.logs")
```

### د) بررسی داده‌ها و استفاده از Nessie

از اینجا به بعد، می‌توانید تمام قابلیت‌های Nessie مانند **branching**، **merging** و **time travel** را که در نسخه قبلی نقشه راه توضیح داده شد، روی جدول `nessie.logs` که داده‌های آن از Elasticsearch آمده است، پیاده‌سازی کنید.

---

## مرحله ۳: نحوه اجرا

1.  فایل `docker-compose.yml` و `roadmap.md` را در ریشه پروژه ایجاد کنید.
2.  پوشه `notebooks` را بسازید.
3.  دستور `docker-compose up -d` را اجرا کنید تا تمام سرویس‌ها راه‌اندازی شوند.
4.  در مرورگر خود آدرس Kibana (`http://localhost:5601`) را باز کرده و داده‌های اولیه را درج کنید.
5.  در مرورگر خود آدرس JupyterLab (`http://localhost:8888`) را باز کنید.
6.  توکن JupyterLab را از لاگ‌های کانتینر `spark-iceberg-nessie` بردارید (`docker logs spark-iceberg-nessie`).
7.  یک نوت‌بوک جدید بسازید و مراحل بالا را اجرا کنید.