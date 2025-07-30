# نقشه راه پروژه: از ETL ساده تا Lakehouse با Iceberg

این پروژه به صورت فازبندی شده، شما را در ساخت یک خط لوله داده از یک ETL ساده تا یک معماری کامل Lakehouse با استفاده از Apache Iceberg راهنمایی می‌کند.

## پیش‌نیازها

*   Docker و Docker Compose باید روی سیستم شما نصب باشند.

## ساختار پروژه

```
/iceberg
|-- docker-compose.yml       # فایل اصلی برای راه‌اندازی تمام سرویس‌ها
|-- phase_1_infrastructure/  # شامل مستندات و اسکریپت‌های مربوط به زیرساخت
|-- phase_2_simple_etl/      # شامل پروژه ETL ساده
|-- roadmap.md               # همین فایل راهنما
```

---

## فاز ۱: راه‌اندازی زیرساخت و درج داده‌های اولیه

**هدف:** آماده‌سازی کامل محیط برای اجرای خط لوله داده.

### گام ۱: راه‌اندازی تمام سرویس‌ها

فایل `docker-compose.yml` در ریشه پروژه قرار دارد. برای راه‌اندازی تمام سرویس‌ها (Elasticsearch, Kibana, MinIO, Nessie, Spark Master, Spark Worker)، دستور زیر را در ترمینال اجرا کنید:

```bash
docker-compose up -d --build
```

### گام ۲: درج داده‌های نمونه در Elasticsearch

پس از راه‌اندازی سرویس‌ها، به **Kibana** (`http://localhost:5601`) بروید، به بخش **Dev Tools** رفته و دستورالعمل‌های موجود در `phase_1_infrastructure/README.md` را برای درج داده‌های نمونه `persons` دنبال کنید.

---

## فاز ۲: اجرای خط لوله ETL ساده

**هدف:** خواندن داده‌ها از Elasticsearch و ذخیره آن‌ها به صورت فایل‌های Parquet در MinIO.

### گام ۱: اجرای اسکریپت Spark

پس از اطمینان از انجام کامل فاز ۱، برای اجرای خط لوله ETL از دستور زیر استفاده کنید:

```bash
docker-compose exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.elasticsearch:elasticsearch-spark-30_2.12:8.4.3 \
  /opt/spark/work-dir/main.py
```

### گام ۲: بررسی نتایج

به رابط کاربری **MinIO** (`http://localhost:9001`) بروید. باید یک باکت به نام `phase-2-warehouse` و داخل آن فایل‌های Parquet را مشاهده کنید.

```