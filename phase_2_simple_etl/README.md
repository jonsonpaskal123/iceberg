# فاز ۲: اجرای یک خط لوله ETL ساده

**هدف:** در این فاز، یک اسکریپت Spark را اجرا می‌کنیم تا داده‌های نمونه `persons` را از Elasticsearch بخواند و آن‌ها را به صورت فایل‌های Parquet در یک باکت مشخص در MinIO ذخیره کند.

---

## پیش‌نیازها

قبل از شروع این فاز، مطمئن شوید که **فاز ۱** را به طور کامل انجام داده‌اید:

۱. سرویس‌های زیرساخت (Elasticsearch, Kibana, MinIO, Nessie) با استفاده از `docker-compose-infra.yml` در حال اجرا هستند.
۲. ایندکس `persons` به همراه ۱۰ رکورد نمونه در Elasticsearch ایجاد شده است.

---

## گام ۱: راه‌اندازی سرویس‌های Spark

در همین پوشه، فایل `docker-compose-spark.yml` قرار دارد. برای راه‌اندازی سرویس‌های Spark (master و worker)، دستور زیر را در ترمینال اجرا کنید:

```bash
docker-compose -f docker-compose-spark.yml up -d --build
```

## گام ۲: اجرای اسکریپت Spark

پس از راه‌اندازی سرویس‌های Spark، برای اجرای خط لوله ETL از دستور زیر استفاده کنید:

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3 \
  /opt/spark/work-dir/main.py
```

**نکته:** در این مرحله، ما فقط از پکیج `elasticsearch-spark` استفاده می‌کنیم، زیرا هنوز با Iceberg و Nessie کاری نداریم.

---

## گام ۳: بررسی نتایج

پس از اجرای موفقیت‌آمیز اسکریپت، نتایج را به صورت زیر بررسی کنید:

*   **در کنسول:** خروجی اجرای Spark باید نشان دهد که ۱۰ رکورد با موفقیت خوانده و در MinIO نوشته شده‌اند.
*   **در MinIO:** به رابط کاربری MinIO (`http://localhost:9001`) بروید. باید یک باکت جدید به نام `phase-2-warehouse` ببینید. داخل این باکت، پوشه‌ای به نام `persons_data` وجود دارد که حاوی فایل‌های Parquet است.

```