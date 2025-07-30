# فاز ۱: راه‌اندازی و آماده‌سازی زیرساخت

**هدف:** در این فاز، تمام سرویس‌های مورد نیاز پروژه را راه‌اندازی کرده و داده‌های اولیه را برای پردازش آماده می‌سازیم.

## گام ۱: راه‌اندازی سرویس‌ها

در همین پوشه، فایل `docker-compose.yml` قرار دارد. برای راه‌اندازی تمام سرویس‌ها (Elasticsearch, Kibana, MinIO, Spark)، دستور زیر را در ترمینال اجرا کنید:

```bash
docker-compose up -d
```

## گام ۲: بررسی دسترسی به سرویس‌ها

بعد از اینکه سرویس‌ها راه‌اندازی شدند، از طریق لینک‌های زیر بررسی کنید که به درستی کار می‌کنند:

*   **Kibana:** `http://localhost:5601`
*   **MinIO Console:** `http://localhost:9001` (Username: `admin`, Password: `password`)

## گام ۳: درج داده‌های نمونه در Elasticsearch

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
