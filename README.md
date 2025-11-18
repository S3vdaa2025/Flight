# Flight Management API

یک سرویس RESTful با FastAPI برای مدیریت داده‌های پرواز با قابلیت‌های CRUD، Pagination، Filtering و Sorting.

## ویژگی‌ها

- ✅ ایجاد، خواندن، به‌روزرسانی و حذف رکوردهای پرواز
- ✅ Pagination برای لیست پروازها
- ✅ Filtering بر اساس فیلدهای مختلف (مبدا، مقصد، وضعیت، نوع هواپیما، تعداد صندلی)
- ✅ Sorting بر اساس فیلدهای مختلف
- ✅ Validation کامل داده‌ها با Pydantic
- ✅ مدیریت خطا و پاسخ‌های استاندارد JSON
- ✅ معماری لایه‌ای (Router, Service, Repository)
- ✅ Type Hints در تمام کد
- ✅ تست‌های واحد با pytest

## ساختار پروژه

```
flight/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database connection and initialization
│   ├── exceptions.py           # Custom exceptions
│   ├── models.py               # Pydantic models
│   ├── schemas.py              # Response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── flights.py          # Flight endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── flight_service.py   # Business logic
│   └── repositories/
│       ├── __init__.py
│       └── flight_repository.py # Data access layer
├── tests/
│   ├── __init__.py
│   └── test_flights.py         # Unit tests
├── requirements.txt
├── README.md
└── flights_sample.json         # Sample data
```

## نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8 یا بالاتر
- pip

### مراحل نصب

1. **کلون کردن یا دانلود پروژه**

```bash
cd flight
```

2. **ایجاد محیط مجازی (اختیاری اما توصیه می‌شود)**

```bash
python -m venv venv

# در Windows
venv\Scripts\activate

# در Linux/Mac
source venv/bin/activate
```

3. **نصب وابستگی‌ها**

```bash
pip install -r requirements.txt
```

4. **راه‌اندازی پایگاه داده**

پایگاه داده SQLite به صورت خودکار در اولین اجرا ایجاد می‌شود. برای ایجاد دستی:

```bash
python -m app.database
```

5. **بارگذاری داده‌های نمونه (اختیاری)**

برای بارگذاری داده‌های نمونه از فایل `flights_sample.json`:

```bash
python scripts/seed_database.py
```

6. **اجرای سرور**

```bash
uvicorn app.main:app --reload
```

سرور در آدرس `http://localhost:8000` اجرا می‌شود.

## مستندات API

پس از اجرای سرور، می‌توانید مستندات تعاملی API را در آدرس‌های زیر مشاهده کنید:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpointها

### 1. ایجاد پرواز جدید

```http
POST /flights
Content-Type: application/json

{
  "flight_number": "SP1001",
  "origin": "JED",
  "destination": "THR",
  "departure_time": "2025-11-08T01:00:00",
  "arrival_time": "2025-11-08T01:57:00",
  "duration_minutes": 57,
  "aircraft_type": "A321",
  "seats_total": 150,
  "seats_available": 26,
  "status": "scheduled",
  "process_id": "P-238"
}
```

**پاسخ موفق:**
```json
{
  "status": "success",
  "message": "Flight created successfully",
  "data": {
    "flight_id": 1,
    ...
  }
}
```

### 2. دریافت لیست پروازها

```http
GET /flights?page=1&page_size=10&origin=JED&status=scheduled&sort_field=departure_time&sort_order=asc
```

**پارامترهای Query:**
- `page`: شماره صفحه (پیش‌فرض: 1)
- `page_size`: تعداد آیتم در هر صفحه (پیش‌فرض: 10، حداکثر: 100)
- `origin`: فیلتر بر اساس فرودگاه مبدا
- `destination`: فیلتر بر اساس فرودگاه مقصد
- `status`: فیلتر بر اساس وضعیت (scheduled, departed, arrived, delayed, cancelled)
- `aircraft_type`: فیلتر بر اساس نوع هواپیما
- `min_seats_available`: حداقل صندلی‌های خالی
- `max_seats_available`: حداکثر صندلی‌های خالی
- `sort_field`: فیلد برای مرتب‌سازی (پیش‌فرض: flight_id)
- `sort_order`: ترتیب مرتب‌سازی (asc یا desc، پیش‌فرض: asc)

**پاسخ:**
```json
{
  "status": "success",
  "message": "Flights retrieved successfully",
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 50,
    "total_pages": 5
  }
}
```

### 3. دریافت پرواز بر اساس ID

```http
GET /flights/{flight_id}
```

### 4. به‌روزرسانی پرواز

```http
PUT /flights/{flight_id}
Content-Type: application/json

{
  "status": "departed",
  "seats_available": 20
}
```

**نکته:** تمام فیلدها اختیاری هستند. فقط فیلدهایی که می‌خواهید به‌روزرسانی شوند را ارسال کنید.

### 5. حذف پرواز

```http
DELETE /flights/{flight_id}
```

## اجرای تست‌ها

برای اجرای تست‌ها:

```bash
pytest tests/ -v
```

یا با نمایش خروجی کامل:

```bash
pytest tests/ -v -s
```

## ساختار پاسخ‌های API

تمام پاسخ‌های API از ساختار استاندارد زیر پیروی می‌کنند:

```json
{
  "status": "success" | "error",
  "message": "پیام توضیحی",
  "data": { ... }
}
```

برای پاسخ‌های Paginated:

```json
{
  "status": "success",
  "message": "پیام توضیحی",
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "total_pages": 10
  }
}
```

## کدهای وضعیت HTTP

- `200 OK`: عملیات موفق
- `201 Created`: ایجاد موفق
- `400 Bad Request`: خطای اعتبارسنجی
- `404 Not Found`: رکورد یافت نشد
- `409 Conflict`: تداخل (مثلاً شماره پرواز تکراری)
- `500 Internal Server Error`: خطای سرور

## مثال‌های استفاده

### ایجاد پرواز جدید

```bash
curl -X POST "http://localhost:8000/flights" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_number": "SP2001",
    "origin": "THR",
    "destination": "JED",
    "departure_time": "2025-12-01T10:00:00",
    "arrival_time": "2025-12-01T11:30:00",
    "duration_minutes": 90,
    "aircraft_type": "A320",
    "seats_total": 180,
    "seats_available": 150,
    "status": "scheduled",
    "process_id": "P-300"
  }'
```

### دریافت پروازها با فیلتر و مرتب‌سازی

```bash
curl "http://localhost:8000/flights?origin=JED&status=scheduled&sort_field=departure_time&sort_order=asc&page=1&page_size=5"
```

### به‌روزرسانی پرواز

```bash
curl -X PUT "http://localhost:8000/flights/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "departed",
    "seats_available": 25
  }'
```

### حذف پرواز

```bash
curl -X DELETE "http://localhost:8000/flights/1"
```

## معماری

این پروژه از معماری لایه‌ای استفاده می‌کند:

1. **Router Layer** (`app/routers/`): مدیریت HTTP requests و responses
2. **Service Layer** (`app/services/`): منطق کسب‌وکار و اعتبارسنجی
3. **Repository Layer** (`app/repositories/`): دسترسی به داده‌ها و عملیات پایگاه داده

این معماری باعث می‌شود:
- کد قابل نگهداری و قابل تست باشد
- لایه‌ها مستقل از یکدیگر باشند
- تغییرات در یک لایه بر لایه‌های دیگر تأثیر نگذارد

## نکات مهم

- پایگاه داده SQLite به صورت خودکار در فایل `flights.db` ایجاد می‌شود
- برای استفاده در محیط Production، توصیه می‌شود از MySQL یا PostgreSQL استفاده کنید
- تمام فیلدهای datetime باید در فرمت ISO 8601 ارسال شوند
- وضعیت پرواز باید یکی از این مقادیر باشد: `scheduled`, `departed`, `arrived`, `delayed`, `cancelled`

## توسعه‌دهندگان

برای افزودن قابلیت‌های جدید:

1. مدل‌های جدید را در `app/models.py` تعریف کنید
2. متدهای Repository را در `app/repositories/` اضافه کنید
3. منطق کسب‌وکار را در `app/services/` پیاده‌سازی کنید
4. Endpointهای جدید را در `app/routers/` اضافه کنید
5. تست‌های مربوطه را در `tests/` بنویسید

## مجوز

این پروژه برای استفاده آموزشی و تجاری آزاد است.

