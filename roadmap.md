# نقشه راه پروژه عملی: خواندن از Elasticsearch و ذخیره در Iceberg

این مستند، نقشه راه فازبندی شده برای ساخت یک پروژه کامل است که در آن داده‌ها از Elasticsearch خوانده شده و در یک جدول Apache Iceberg با استفاده از کاتالوگ Nessie ذخیره می‌شوند.

---

## فاز ۱: راه‌اندازی زیرساخت

**هدف:** در این فاز، تمام سرویس‌های مورد نیاز پروژه را راه‌اندازی کرده و از صحت عملکرد آن‌ها اطمینان حاصل می‌کنیم.

### گام ۱: راه‌اندازی سرویس‌ها با Docker Compose

فایل `docker-compose.yml` در ریشه پروژه از قبل موجود است. برای راه‌اندازی تمام سرویس‌ها (Elasticsearch, Kibana, Nessie, MinIO, Spark)، دستور زیر را در ترمینال اجرا کنید:

```bash
docker-compose up -d
```

### گام ۲: بررسی دسترسی به سرویس‌ها

بعد از اینکه سرویس‌ها راه‌اندازی شدند، از طریق لینک‌های زیر بررسی کنید که به درستی کار می‌کنند:

*   **Kibana (برای دیدن داده‌های Elasticsearch):** `http://localhost:5601`
*   **MinIO Console (برای دیدن فایل‌های ذخیره شده):** `http://localhost:9001` (Username: `admin`, Password: `password`)
*   **Nessie UI (برای دیدن شاخه‌ها و کامیت‌ها):** `http://localhost:19120`

---

## فاز ۲: اجرای اولین خط لوله ETL

**هدف:** در این فاز، یک خط لوله کامل را برای انتقال داده‌های نمونه از مبدا (Elasticsearch) به مقصد (جدول Iceberg) اجرا می‌کنیم.

### گام ۱: درج داده‌های نمونه در Elasticsearch

به رابط کاربری **Kibana** بروید، به بخش **Dev Tools** رفته و دستورات زیر را برای ایجاد ایندکس `persons` و درج ۱۰ رکورد نمونه اجرا کنید.

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

### گام ۲: اجرای اسکریپت Spark

برای اجرای خط لوله ETL که داده‌ها را از Elasticsearch خوانده و در جدول Iceberg می‌نویسد، از دستور زیر استفاده کنید:

```bash
docker exec spark-runner spark-submit \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.75.0 \
  /home/jovyan/work/iceberg_project/main.py
```

### گام ۳: بررسی نتایج

*   **در MinIO:** به رابط کاربری MinIO بروید. باید یک باکت به نام `warehouse` و در داخل آن، پوشه‌ای به نام `persons` را ببینید.
*   **در Nessie:** به رابط کاربری Nessie بروید. باید یک کامیت جدید در شاخه `main` ببینید که نشان‌دهنده ایجاد جدول `persons` است.
*   **در کنسول:** خروجی اجرای Spark باید نشان دهد که ۱۰ رکورد با موفقیت خوانده و نوشته شده‌اند.

---

## فاز ۳: کار با قابلیت‌های پیشرفته Iceberg

**هدف:** در این فاز، با سه قابلیت کلیدی آیسبرگ یعنی افزودن داده، سفر در زمان و تکامل اسکما به صورت عملی کار می‌کنیم.

### گام ۱: افزودن داده‌های جدید (Append)

چند رکورد جدید در Elasticsearch درج کرده و اسکریپت Spark را دوباره اجرا کنید. مشاهده خواهید کرد که داده‌های جدید به جدول اضافه می‌شوند و یک کامیت جدید در Nessie ثبت می‌گردد.

### گام ۲: سفر در زمان (Time Travel)

با استفاده از شناسه یک کامیت قدیمی از رابط کاربری Nessie، می‌توانید نسخه‌های قبلی جدول را کوئری بزنید و ببینید که داده‌ها در آن زمان چگونه بوده‌اند.

### گام ۳: تکامل اسکما (Schema Evolution)

یک ستون جدید (مثلاً `country`) به داده‌های خود در Elasticsearch اضافه کنید. سپس با افزودن آپشن `mergeSchema` به کد Spark، اسکریپت را دوباره اجرا کنید. خواهید دید که اسکما جدول بدون نیاز به بازنویسی کل داده‌ها، به‌روز می‌شود.

```