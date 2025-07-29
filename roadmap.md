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
/iceberg
|-- docker-compose.yml
|-- iceberg_project/
|   |-- __init__.py
|   |-- config.py
|   |-- elastic_reader.py
|   |-- iceberg_writer.py
|   `-- main.py
`-- roadmap.md
```

---

## مرحله ۱: ایجاد فایل Docker Compose

محتوای فایل `docker-compose.yml` را به شکل زیر ایجاد می‌کنیم. سرویس Spark طوری تنظیم می‌شود که همیشه در حال اجرا باقی بماند تا بتوانیم اسکریپت خود را در آن اجرا کنیم. (این فایل از قبل موجود است)

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
      - ./iceberg_project:/home/jovyan/work/iceberg_project
    command: tail -f /dev/null
```

---

## مرحله ۲: بالا آوردن سرویس‌ها

با استفاده از دستور زیر، تمام سرویس‌ها را راه‌اندازی می‌کنیم. (این مرحله قبلاً انجام شده است)

```bash
docker-compose up -d
```

---

## مرحله ۲.۵: دسترسی به سرویس‌ها

بعد از اینکه سرویس‌ها راه‌اندازی شدند، می‌توانید از طریق لینک‌های زیر به آن‌ها دسترسی داشته باشید:

*   **Kibana (برای دیدن داده‌های Elasticsearch):** `http://localhost:5601`
*   **MinIO Console (برای دیدن فایل‌های ذخیره شده):** `http://localhost:9001` (Username: `admin`, Password: `password`)
*   **Nessie UI (برای دیدن شاخه‌ها و کامیت‌ها):** `http://localhost:19120`

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

## مرحله ۴: اجرای اسکریپت Spark

اسکریپت اصلی Spark در مسیر `iceberg_project/main.py` قرار دارد. این اسکریپت داده‌ها را از Elasticsearch می‌خواند و در Iceberg ذخیره می‌کند.

---

## مرحله ۵: نحوه اجرا

1.  فایل `docker-compose.yml` در ریشه پروژه موجود است.
2.  پوشه `iceberg_project` حاوی اسکریپت‌های پایتون است.
3.  دستور `docker-compose up -d` را اجرا کنید تا تمام سرویس‌ها راه‌اندازی شوند. (این مرحله قبلاً انجام شده است)
4.  با استفاده از Kibana (`http://localhost:5601`) داده‌های اولیه را در Elasticsearch درج کنید. (این مرحله را باید خودتان انجام دهید)
5.  اسکریپت Spark را با دستور زیر اجرا کنید:
    ```bash
    docker exec spark-runner spark-submit \
      --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.75.0 \
      /home/jovyan/work/iceberg_project/main.py
    ```

```