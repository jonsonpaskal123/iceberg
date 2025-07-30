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

## مرحله ۲: درج داده‌های نمونه افراد در Elasticsearch

به آدرس `http://localhost:5601` بروید تا به Kibana دسترسی پیدا کنید. سپس به بخش **Dev Tools** رفته و دستورات زیر را برای ایجاد ایندکس و درج ۱۰ رکورد نمونه از افراد اجرا کنید.

```json
# ایجاد ایندکس با نگاشت (mapping) صحیح
PUT /persons
{
  "mappings": {
    "properties": {
      "person_id": { "type": "integer" },
      "first_name": { "type": "text" },
      "last_name": { "type": "text" },
      "email": { "type": "keyword" },
      "city": { "type": "keyword" }
    }
  }
}

# درج ۱۰ رکورد نمونه با استفاده از Bulk API
POST /persons/_bulk
{ "index": { "_id": "1" } }
{ "person_id": 1, "first_name": "آرش", "last_name": "رضایی", "email": "arash.rezaei@example.com", "city": "تهران" }
{ "index": { "_id": "2" } }
{ "person_id": 2, "first_name": "سارا", "last_name": "محمدی", "email": "sara.mohammadi@example.com", "city": "اصفهان" }
{ "index": { "_id": "3" } }
{ "person_id": 3, "first_name": "علی", "last_name": "احمدی", "email": "ali.ahmadi@example.com", "city": "شیراز" }
{ "index": { "_id": "4" } }
{ "person_id": 4, "first_name": "مریم", "last_name": "حسینی", "email": "maryam.hosseini@example.com", "city": "تهران" }
{ "index": { "_id": "5" } }
{ "person_id": 5, "first_name": "رضا", "last_name": "کریمی", "email": "reza.karimi@example.com", "city": "مشهد" }
{ "index": { "_id": "6" } }
{ "person_id": 6, "first_name": "فاطمه", "last_name": "صادقی", "email": "fatemeh.sadeghi@example.com", "city": "تبریز" }
{ "index": { "_id": "7" } }
{ "person_id": 7, "first_name": "حسین", "last_name": "مرادی", "email": "hossein.moradi@example.com", "city": "اصفهان" }
{ "index": { "_id": "8" } }
{ "person_id": 8, "first_name": "زهرا", "last_name": "جعفری", "email": "zahra.jafari@example.com", "city": "شیراز" }
{ "index": { "_id": "9" } }
{ "person_id": 9, "first_name": "مهدی", "last_name": "کاظمی", "email": "mehdi.kazemi@example.com", "city": "تهران" }
{ "index": { "_id": "10" } }
{ "person_id": 10, "first_name": "نگار", "last_name": "قاسمی", "email": "negar.ghasemi@example.com", "city": "کرج" }
```

---

## مرحله ۳: اجرای خط لوله ETL

اسکریپت اصلی Spark در مسیر `iceberg_project/main.py` قرار دارد. این اسکریپت داده‌ها را از ایندکس `persons` در Elasticsearch می‌خواند و در جدول آیسبرگ ذخیره می‌کند.

برای اجرای اسکریپت، از دستور زیر استفاده کنید:

```bash
docker exec spark-runner spark-submit \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.75.0 \
  /home/jovyan/work/iceberg_project/main.py
```

---

## مرحله ۴: بررسی نتایج

*   **در MinIO:** به آدرس `http://localhost:9001` بروید. باید یک باکت به نام `warehouse` و در داخل آن، پوشه‌ای به نام `persons` را ببینید که حاوی فایل‌های داده جدول آیسبرگ است.
*   **در Nessie:** به آدرس `http://localhost:19120` بروید. باید یک کامیت جدید در شاخه `main` ببینید که نشان‌دهنده ایجاد جدول `persons` است.
*   **در کنسول:** خروجی اجرای Spark باید نشان دهد که داده‌ها با موفقیت خوانده و نوشته شده‌اند و در مرحله تأیید، ۱۰ رکوردی که درج کرده‌اید نمایش داده می‌شوند.

---

## مرحله ۵: افزودن داده‌های جدید

برای تست قابلیت‌های آیسبرگ، چند رکورد جدید در Elasticsearch درج کنید:

```json
POST /persons/_bulk
{ "index": { "_id": "11" } }
{ "person_id": 11, "first_name": "کیان", "last_name": "اکبری", "email": "kian.akbari@example.com", "city": "اهواز" }
{ "index": { "_id": "12" } }
{ "person_id": 12, "first_name": "هستی", "last_name": "نوری", "email": "hasti.nouri@example.com", "city": "رشت" }
```

سپس اسکریپت Spark را در **مرحله ۳ دوباره** اجرا کنید.

**چه اتفاقی می‌افتد؟**

*   آیسبرگ به طور خودکار داده‌های جدید را به جدول اضافه می‌کند (`append`).
*   یک کامیت جدید در Nessie ثبت می‌شود.
*   در خروجی Spark، باید هر ۱۲ رکورد را ببینید.

---

## مرحله ۶: سفر در زمان (Time Travel)

برای مشاهده قدرت آیسبرگ، می‌توانید به نسخه قبلی جدول برگردید. ابتدا باید شناسه کامیت (Commit ID) قدیمی را از رابط کاربری Nessie پیدا کنید.

سپس می‌توانید از `spark-shell` استفاده کنید تا به نسخه قبلی دسترسی پیدا کنید:

```python
# مثال برای خواندن از یک کامیت خاص
df = spark.read \
    .option("as-of-commit", "<COMMIT_ID_FROM_NESSIE>") \
    .table("nessie.persons")

df.show()
```

این کوئری فقط ۱۰ رکورد اولیه را به شما نشان خواهد داد.

---

## مرحله ۷: تکامل اسکما (Schema Evolution)

فرض کنید می‌خواهیم یک ستون جدید به نام `country` به جدول اضافه کنیم.

1.  **یک رکورد جدید با فیلد `country` در Elasticsearch درج کنید:**
    ```json
    POST /persons/_doc
    { "person_id": 13, "first_name": "ماهان", "last_name": "صالحی", "email": "mahan.salehi@example.com", "city": "یزد", "country": "ایران" }
    ```

2.  **اسکریپت Spark را برای ادغام اسکما تغییر دهید:**
    این کار با افزودن یک آپشن به دستور `write` در فایل `iceberg_writer.py` انجام می‌شود.
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

*   جدول `persons` حالا یک ستون جدید به نام `country` دارد.
*   رکوردهای قدیمی در این ستون مقدار `null` خواهند داشت.
*   رکورد جدید مقدار `ایران` را خواهد داشت.