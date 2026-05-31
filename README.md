# DRF E-Commerce API

A production-style E-Commerce REST API built with Django REST Framework.

This project focuses on clean architecture, service-layer business logic, authentication, order management, payment workflow, and scalable backend design principles.

---

# Features

* JWT Authentication
* User Registration & Activation
* Product Catalog
* Category System
* Product Reviews & Ratings
* Shopping Cart
* Wishlist
* Checkout System
* Coupon System
* Payment Workflow
* Order Management
* Swagger API Documentation
* Dockerized Development Environment
* Service Layer Architecture

---

# Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Docker
* JWT Authentication
* DRF-YASG (Swagger)
* Redis (planned)
* Celery (planned)

---

# Project Structure

```bash
apps/
├── accounts/
├── catalog/
├── cart/
├── orders/
├── payment/
└── reviews/
```

---

# Architecture Notes

This project uses a service-layer approach for handling complex business logic such as:

* checkout flow
* coupon validation
* payment verification
* stock management

The goal was to avoid fat serializers and overloaded views while keeping the codebase maintainable and scalable.

---

# Main Workflows

## Checkout Flow

```text
Cart → Checkout → Order Creation → Payment Creation → Payment Verification
```

## Payment Verification

After successful payment verification:

* payment status updates
* order status updates
* stock decreases
* coupon usage updates
* cart clears automatically

---

# API Documentation

Swagger UI:

```text
/api/schema/swagger-ui/
```

---

# Running the Project

## Clone the repository

```bash
git clone https://github.com/parsabarari/Drf-ECommerce-API.git
cd Drf-ECommerce-API
```

---

## Run with Docker

```bash
docker-compose up --build
```

---

## Apply migrations

```bash
docker-compose exec backend python manage.py migrate
```

---

## Create superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

---

# Future Improvements

* Celery & Redis integration
* Async email sending
* Automated testing
* CI/CD pipeline
* Advanced filtering & caching
* Production deployment

---

# Author

Parsa Barari
