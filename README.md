# DRF E-Commerce API

A modular e-commerce backend built with **Django** and **Django REST Framework**, featuring phone number authentication via OTP, JWT-based authorization, product catalog management, shopping cart, checkout, payment integration, reviews, and administrative tools.

The project follows a service-oriented architecture where core business logic is encapsulated in dedicated service modules rather than view logic, making the codebase easier to maintain and extend.

> **Project Status:** Active development. Some infrastructure and authentication features are partially implemented or planned.

---

# Features

## Authentication

* Phone-number based custom user model
* OTP login and registration flow via SMS
* JWT access and refresh tokens
* OTP request throttling
* Iranian mobile number validation
* Automatic profile creation

## User Profiles

* Retrieve authenticated profile
* Update profile information
* Profile image support

## Product Catalog

* Product categories
* Product listing
* Product detail by slug
* Draft/published product visibility
* Product images
* Product stock management
* Discount pricing logic
* Average product ratings

## Search & Filtering

* Full-text product search
* Category filtering
* Ordering
* Pagination

## Wishlist

* Toggle products in personal wishlist

## Shopping Cart

* User-specific shopping cart
* Add products
* Update quantities
* Delete items
* Clear cart
* Stock validation
* Automatic quantity merging
* Cart total calculation

## Orders

* Checkout from cart
* Order creation
* User order history
* Order details
* Shipping address support

## Coupons

* Coupon validation
* Expiration support
* Usage limits
* One-use-per-user validation

> Coupon usage tracking exists but is not fully integrated into the payment success workflow.

## Payments

* Zarinpal payment gateway integration
* Payment verification
* Callback endpoint
* Payment history
* Order completion after successful payment
* Inventory reduction after payment
* Automatic cart clearing after payment

## Reviews

* Product reviews
* One review per user per product
* Rating (1–5)
* Review moderation
* Ownership permissions
* Automatic product rating updates

## API Documentation

* Swagger UI
* ReDoc
* OpenAPI schema generation

## Administration

Django Admin interfaces are available for:

* Users
* Profiles
* Products
* Categories
* Wishlist
* Cart
* Orders
* Coupons
* Payments
* Reviews

---

# Tech Stack

## Backend

* Python
* Django 6
* Django REST Framework

## Database

* PostgreSQL

## Authentication

* SimpleJWT
* DRF Token Authentication (legacy)
* Session Authentication
* Basic Authentication

## Documentation

* drf-yasg (Swagger / ReDoc)

## Image Handling

* Pillow

## Email

* django-templated-email
* smtp4dev (development)

## External Services

* SMS.ir
* Zarinpal Payment Gateway

## Development

* Docker
* Docker Compose
* Gunicorn
* Nginx
* Faker
* factory-boy
* pytest
* pytest-django

---

# Architecture Overview

The project is organized into independent Django applications with business logic extracted into dedicated service modules.

```
Client
    │
    ▼
Django REST Framework API
    │
    ├── Accounts
    ├── Catalog
    ├── Cart
    ├── Orders
    ├── Payments
    └── Reviews
           │
           ▼
      Service Layer
           │
           ▼
     PostgreSQL Database
```

Major design decisions include:

* Phone-number-first authentication
* OTP login doubles as user registration
* Checkout creates pending orders
* Inventory changes occur only after successful payment
* Reviews require moderation before affecting ratings
* Service-layer architecture for checkout, payments, coupons, cart operations, and ratings

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Optionally populate the database with sample data:

```bash
python manage.py insert_data
```

Run the development server:

```bash
python manage.py runserver
```

---

# Environment Variables

The project uses environment variables for configuration.

The extracted inventory confirms variables for PostgreSQL and Zarinpal integration, but does **not** provide a complete `.env` specification.

Known variables include:

```env
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
ZARINPAL_REQUEST_URL=
```

Additional environment variables may exist but cannot be confirmed from the available inventory.

---

# Docker Setup

Development environments are provided using Docker Compose.

Available configurations include:

* PostgreSQL
* Django backend
* smtp4dev
* Nginx (stage configuration)
* Gunicorn (stage configuration)

Example:

```bash
docker compose -f docker-compose-stage.yml up --build
```

or

```bash
docker compose -f docker-compose-prod.yml up --build
```

---

# Local Development

Run migrations:

```bash
python manage.py migrate
```

Create sample data:

```bash
python manage.py insert_data
```

Run the server:

```bash
python manage.py runserver
```

---

# Running Tests

The repository includes:

* pytest
* pytest-django
* factory-boy

Run tests with:

```bash
pytest
```

**Current Status**

Static inspection indicates that portions of the test suite are outdated relative to the current authentication and payment implementation. Some payment tests also reference an older mock payment workflow.

---

# API Overview

## Authentication

| Method | Endpoint                        |
| ------ | ------------------------------- |
| POST   | `/accounts/api/v1/otp/request/` |
| POST   | `/accounts/api/v1/otp/verify/`  |

## Profile

| Method | Endpoint                            |
| ------ | ----------------------------------- |
| GET    | `/accounts/api/v1/profile/profile/` |
| PATCH  | `/accounts/api/v1/profile/profile/` |
| PUT    | `/accounts/api/v1/profile/profile/` |

## Catalog

* Categories
* Category details
* Category products
* Product list
* Product detail
* Wishlist toggle

## Cart

* Retrieve cart
* CRUD cart items
* Clear cart

## Orders

* Checkout
* List orders
* Retrieve order

## Payments

* Create payment
* Verify payment
* Payment callback
* List payments
* Payment details

## Reviews

* CRUD review endpoints

## Documentation

* `/swagger/`
* `/redoc/`

---

# Project Structure

```
core/
│
├── accounts/
├── catalog/
├── cart/
├── orders/
├── payment/
├── reviews/
├── core/
│
├── Dockerfiles
├── docker-compose files
└── nginx configuration
```

---

# Deployment

The repository includes infrastructure for deployment using:

* Docker
* Gunicorn
* Nginx
* PostgreSQL

Production deployment exists in an initial form, but the extracted inventory indicates additional production hardening is still required.

---

# Security Notes

Implemented:

* JWT authentication
* OTP expiration
* OTP brute-force protection
* OTP throttling
* Object-level permissions
* Staff-only draft product visibility
* Coupon validation
* Iranian phone number validation

Known issues identified from the extracted inventory:

* `DEBUG=True`
* Hardcoded Django `SECRET_KEY`
* Hardcoded SMS API key
* Empty `ALLOWED_HOSTS`
* OTP stored in local memory cache instead of Redis
* OTP printed to the console
* Multiple authentication mechanisms enabled simultaneously (JWT, Session, Basic, Token)
* Static/media configuration requires correction

---

# Roadmap

The following items are based solely on partially implemented or planned functionality identified in the project inventory:

* Redis-backed caching
* Celery integration
* Background jobs
* Asynchronous email sending
* CI/CD pipeline
* Improved caching strategy
* Advanced filtering
* Address CRUD API
* Password reset flow
* Production deployment hardening

---

# Contributing

Contributions are welcome.

Please consider the following workflow:

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Add or update tests where applicable.
5. Submit a pull request with a clear description of the changes.

---

# License

License information is currently **unknown**.

Replace this section with the appropriate license before publishing the repository.
