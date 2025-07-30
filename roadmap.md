# نقشه راه پروژه: از ETL ساده تا Lakehouse با Iceberg

این پروژه به صورت گام به گام، شما را در ساخت یک خط لوله داده از یک ETL ساده تا یک معماری کامل Lakehouse با استفاده از Apache Iceberg راهنمایی می‌کند.

## پیش‌نیازها

*   Docker و Docker Compose باید روی سیستم شما نصب باشند.

## گام ۱: راه‌اندازی زیرساخت و درج داده‌های اولیه

**هدف:** آماده‌سازی کامل محیط برای اجرای خط لوله داده.

### ۱. راه‌اندازی تمام سرویس‌ها

فایل `docker-compose.yml` در ریشه پروژه قرار دارد. برای راه‌اندازی تمام سرویس‌ها (Elasticsearch, Kibana, MinIO, Nessie, Spark Master, Spark Worker)، دستور زیر را در ترمینال اجرا کنید:

```bash
docker-compose up -d --build
```

### ۲. درج داده‌های نمونه در Elasticsearch

پس از راه‌اندازی سرویس‌ها، به **Kibana** (`http://localhost:5601`) بروید، به بخش **Dev Tools** رفته و دستورات زیر را برای ایجاد ایندکس `persons` و درج ۱۰ رکورد نمونه اجرا کنید.

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
      "code_melli": { "type": "keyword" },
      "city": { "type": "keyword" }
    }
  }
}

# درج ۱۰ رکورد نمونه با استفاده از Bulk API
POST /persons/_bulk
{ "index": { "_id": "1" } }
{ "person_id": 1, "first_name": "آرش", "last_name": "رضایی", "email": "arash.rezaei@example.com", "code_melli": "0012345678", "city": "تهران" }
{ "index": { "_id": "2" } }
{ "person_id": 2, "first_name": "سارا", "last_name": "محمدی", "email": "sara.mohammadi@example.com", "code_melli": "0023456789", "city": "اصفهان" }
{ "index": { "_id": "3" } }
{ "person_id": 3, "first_name": "علی", "last_name": "احمدی", "email": "ali.ahmadi@example.com", "code_melli": "0034567890", "city": "شیراز" }
{ "index": { "_id": "4" } }
{ "person_id": 4, "first_name": "مریم", "last_name": "حسینی", "email": "maryam.hosseini@example.com", "code_melli": "0045678901", "city": "تهران" }
{ "index": { "_id": "5" } }
{ "person_id": 5, "first_name": "رضا", "last_name": "کریمی", "email": "reza.karimi@example.com", "code_melli": "0056789012", "city": "مشهد" }
{ "index": { "_id": "6" } }
{ "person_id": 6, "first_name": "فاطمه", "last_name": "صادقی", "email": "fatemeh.sadeghi@example.com", "code_melli": "0067890123", "city": "تبریز" }
{ "index": { "_id": "7" } }
{ "person_id": 7, "first_name": "حسین", "last_name": "مرادی", "email": "hossein.moradi@example.com", "code_melli": "0078901234", "city": "اصفهان" }
{ "index": { "_id": "8" } }
{ "person_id": 8, "first_name": "زهرا", "last_name": "جعفری", "email": "zahra.jafari@example.com", "code_melli": "0089012345", "city": "شیراز" }
{ "index": { "_id": "9" } }
{ "person_id": 9, "first_name": "مهدی", "last_name": "کاظمی", "email": "mehdi.kazemi@example.com", "code_melli": "0090123456", "city": "تهران" }
{ "index": { "_id": "10" } }
{ "person_id": 10, "first_name": "نگار", "last_name": "قاسمی", "email": "negar.ghasemi@example.com", "code_melli": "0101234567", "city": "کرج" }
```

## گام ۲: اجرای خط لوله ETL ساده

**هدف:** خواندن داده‌ها از Elasticsearch و ذخیره آن‌ها به صورت فایل‌های Parquet در MinIO.

### ۱. اجرای اسکریپت Spark

پس از اطمینان از انجام کامل گام ۱، برای اجرای خط لوله ETL از دستور زیر استفاده کنید:

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3 \
  /opt/spark/work-dir/main.py
```

### ۲. بررسی نتایج

به رابط کاربری **MinIO** (`http://localhost:9001`) بروید. باید یک باکت به نام `phase-2-warehouse` و داخل آن فایل‌های Parquet را مشاهده کنید.

```