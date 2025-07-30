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

## مرحله ۱: راه‌اندازی محیط و دسترسی به سرویس‌ها

فایل `docker-compose.yml` در ریشه پروژه از قبل موجود است. برای راه‌اندازی تمام سرویس‌ها، دستور زیر را در ترمینال اجرا کنید:

```bash
docker-compose up -d
```

بعد از اینکه سرویس‌ها راه‌اندازی شدند، می‌توانید از طریق لینک‌های زیر به آن‌ها دسترسی داشته باشید:

*   **Kibana (برای دیدن داده‌های Elasticsearch):** `http://localhost:5601`
*   **MinIO Console (برای دیدن فایل‌های ذخیره شده):** `http://localhost:9001` (Username: `admin`, Password: `password`)
*   **Nessie UI (برای دیدن شاخه‌ها و کامیت‌ها):** `http://localhost:19120`

---

## مرحله ۲: درج داده‌های نمونه در Elasticsearch

به آدرس `http://localhost:5601` بروید تا به Kibana دسترسی پیدا کنید. سپس به بخش **Dev Tools** رفته و دستورات زیر را برای ایجاد ایندکس و درج داده‌های نمونه اجرا کنید.

```json
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

## مرحله ۳: اجرای خط لوله ETL

اسکریپت اصلی Spark در مسیر `iceberg_project/main.py` قرار دارد. این اسکریپت داده‌ها را از Elasticsearch می‌خواند و در جدول آیسبرگ ذخیره می‌کند.

برای اجرای اسکریپت، از دستور زیر استفاده کنید:

```bash
docker exec spark-runner spark-submit \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.75.0 \
  /home/jovyan/work/iceberg_project/main.py
```

---

## مرحله ۴: بررسی نتایج

*   **در MinIO:** به آدرس `http://localhost:9001` بروید. باید یک باکت به نام `warehouse` و در داخل آن، پوشه‌ای به نام `logs` را ببینید که حاوی فایل‌های داده (Parquet) و فراداده (Avro, JSON) جدول آیسبرگ است.
*   **در Nessie:** به آدرس `http://localhost:19120` بروید. باید یک کامیت جدید در شاخه `main` ببینید که نشان‌دهنده ایجاد جدول `logs` است.
*   **در کنسول:** خروجی اجرای Spark باید نشان دهد که داده‌ها با موفقیت خوانده و نوشته شده‌اند و در مرحله تأیید، دو رکوردی که درج کرده‌اید نمایش داده می‌شوند.

---

## مرحله ۵: افزودن داده‌های جدید

برای تست قابلیت‌های آیسبرگ، چند رکورد جدید در Elasticsearch درج کنید:

```json
POST /app_logs/_doc
{ "ts": "2023-10-27T11:00:00Z", "level": "INFO", "message": "Payment processed" }

POST /app_logs/_doc
{ "ts": "2023-10-27T11:15:00Z", "level": "ERROR", "message": "Failed to connect to database" }
```

سپس اسکریپت Spark را در **مرحله ۳ دوباره** اجرا کنید.

**چه اتفاقی می‌افتد؟**

*   آیسبرگ به طور خودکار داده‌های جدید را به جدول اضافه می‌کند (`append`).
*   یک کامیت جدید در Nessie ثبت می‌شود.
*   در خروجی Spark، باید هر چهار رکورد را ببینید.

---

## مرحله ۶: سفر در زمان (Time Travel)

برای مشاهده قدرت آیسبرگ، می‌توانید به نسخه قبلی جدول برگردید. ابتدا باید شناسه کامیت (Commit ID) قدیمی را از رابط کاربری Nessie یا از طریق API آن پیدا کنید.

سپس می‌توانید یک اسکریپت Spark جدید بنویسید یا از `spark-shell` استفاده کنید تا به نسخه قبلی دسترسی پیدا کنید:

```python
# مثال برای خواندن از یک کامیت خاص
df = spark.read \
    .option("as-of-commit", "<COMMIT_ID_FROM_NESSIE>") \
    .table("nessie.logs")

df.show()
```

این کوئری فقط دو رکورد اولیه را به شما نشان خواهد داد.

---

## مرحله ۷: تکامل اسکما (Schema Evolution)

فرض کنید می‌خواهیم یک ستون جدید به نام `hostname` به جدول اضافه کنیم.

1.  **یک رکورد جدید با فیلد `hostname` در Elasticsearch درج کنید:**
    ```json
    POST /app_logs/_doc
    { "ts": "2023-10-27T12:00:00Z", "level": "INFO", "message": "New server online", "hostname": "server-01" }
    ```

2.  **اسکریپت Spark را برای ادغام اسکما تغییر دهید:**
    قبل از نوشتن داده، باید به Spark بگویید که اسکما را ادغام کند. این کار با افزودن یک آپشن به دستور `write` انجام می‌شود. **(توجه: این تغییر باید در کد `iceberg_writer.py` اعمال شود)**
    ```python
    # در فایل iceberg_writer.py
    df.write \
      .format("iceberg") \
      .option("mergeSchema", "true") \ # این خط را اضافه کنید
      .mode("append") \
      .save(table_name)
    ```

3.  **اسکریپت را دوباره اجرا کنید.**

**نتیجه:**

*   جدول `logs` حالا یک ستون جدید به نام `hostname` دارد.
*   رکوردهای قدیمی در این ستون مقدار `null` خواهند داشت.
*   رکورد جدید مقدار `server-01` را خواهد داشت.
*   این تغییر بدون نیاز به بازنویسی کل جدول انجام می‌شود.
