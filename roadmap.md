# نقشه راه پروژه عملی آیسبرگ و Nessie

این مستند، نقشه راه گام به گام برای ساخت یک پروژه کوچک اما کامل با استفاده از Apache Iceberg و کاتالوگ Nessie است. هدف این است که تمام مفاهیمی که یاد گرفتیم را در یک سناریوی واقعی پیاده‌سازی کنیم.

**پشته تکنولوژی (Technology Stack):**

*   **پردازش:** Apache Spark
*   **فرمت جدول:** Apache Iceberg
*   **کاتالوگ:** Nessie (برای قابلیت‌های Git-مانند)
*   **ذخیره‌سازی:** MinIO (به عنوان یک Object Storage سازگار با S3)
*   **ارکستراسیون:** Docker Compose (برای راه‌اندازی تمام سرویس‌ها)

---

## ساختار پروژه

ابتدا، ساختار پوشه‌های پروژه را به شکل زیر ایجاد می‌کنیم:

```
/iceberg-nessie-project
|-- docker-compose.yml
|-- notebooks/
|   `-- 01-iceberg-nessie-demo.ipynb
`-- roadmap.md
```

*   `docker-compose.yml`: برای تعریف و راه‌اندازی سرویس‌های Nessie، MinIO و Spark.
*   `notebooks/`: نوت‌بوک‌های Jupyter که کدهای Spark ما در آن قرار می‌گیرد.

---

## مرحله ۱: راه‌اندازی زیرساخت با Docker Compose

محتوای فایل `docker-compose.yml` را به شکل زیر ایجاد می‌کنیم. این فایل تمام سرویس‌های مورد نیاز ما را با تنظیمات صحیح راه‌اندازی می‌کند.

```yaml
version: '3'

services:
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

یک نوت‌بوک جدید در پوشه `notebooks` به نام `01-iceberg-nessie-demo.ipynb` ایجاد کرده و کدهای زیر را در سلول‌های جداگانه اجرا می‌کنیم.

### الف) اتصال و بررسی Nessie

برای اطمینان از اینکه Spark به درستی به Nessie متصل شده است، لیست شاخه‌ها (references) را می‌گیریم.

```sql
-- In a SQL cell
LIST REFERENCES IN nessie;
```

### ب) ایجاد جدول آیسبرگ

یک جدول برای ذخیره لاگ‌ها با پارتیشن‌بندی بر اساس سطح لاگ (`level`) ایجاد می‌کنیم.

```sql
CREATE TABLE nessie.logs (
  ts TIMESTAMP,
  level STRING,
  message STRING
)
PARTITIONED BY (level);
```

### ج) درج داده‌های اولیه

چند رکورد اولیه در شاخه `main` درج می‌کنیم.

```sql
INSERT INTO nessie.logs VALUES
(current_timestamp(), 'INFO', 'User logged in'),
(current_timestamp(), 'WARNING', 'Disk space is running low'),
(current_timestamp(), 'INFO', 'Data processed successfully');
```

### د) استفاده از شاخه‌ها (Branching) برای ETL

حالا قدرت واقعی Nessie را نمایش می‌دهیم. یک شاخه جدید برای فرآیند ETL ایجاد می‌کنیم.

```sql
-- Create a new branch for our ETL job
CREATE BRANCH etl_branch IN nessie;

-- Switch to the new branch
USE REFERENCE etl_branch IN nessie;

-- Insert new data only in this branch
INSERT INTO nessie.logs VALUES
(current_timestamp(), 'ERROR', 'Failed to connect to database'),
(current_timestamp(), 'INFO', 'New data batch arrived');
```

حالا اگر به شاخه `main` برگردیم، می‌بینیم که داده‌های جدید در آن وجود ندارند.

```sql
USE REFERENCE main IN nessie;
SELECT * FROM nessie.logs;
```

### ه) ادغام (Merge) شاخه

پس از تایید داده‌های جدید، شاخه `etl_branch` را با `main` ادغام می‌کنیم.

```sql
MERGE BRANCH etl_branch INTO main IN nessie;
```

### و) سفر در زمان (Time Travel)

می‌توانیم وضعیت جدول را قبل از ادغام مشاهده کنیم.

```sql
-- Find the commit hash before the merge
LIST REFERENCES IN nessie;

-- Query the table at a specific commit
SELECT * FROM nessie.logs VERSION AS OF 'some_commit_hash_before_merge';
```

### ز) تکامل طرح‌واره (Schema Evolution)

یک ستون جدید به جدول اضافه می‌کنیم بدون اینکه نیاز به بازنویسی داده‌ها باشد.

```sql
ALTER TABLE nessie.logs ADD COLUMN source_ip STRING;
```

---

## مرحله ۳: نحوه اجرا

1.  فایل `docker-compose.yml` و `roadmap.md` را در ریشه پروژه ایجاد کنید.
2.  پوشه `notebooks` را بسازید.
3.  دستور `docker-compose up -d` را اجرا کنید تا تمام سرویس‌ها راه‌اندازی شوند.
4.  در مرورگر خود آدرس `http://localhost:8888` را باز کنید.
5.  توکن JupyterLab را از لاگ‌های کانتینر `spark-iceberg-nessie` بردارید (`docker logs spark-iceberg-nessie`).
6.  یک نوت‌بوک جدید بسازید و مراحل بالا را اجرا کنید.
