# Vastarion Hunter - Price Tracking API

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-blue)
![Redis](https://img.shields.io/badge/Redis-cache-red)
![Docker](https://img.shields.io/badge/Docker-containerized-blue)

Track product prices across e-commerce platforms and get notified when prices drop below your target.
## Features

- **User Authentication** - JWT-based register/login system
- **Product Tracking** - Add product URLs to track prices
- **Price History** - View historical price data for any product
- **Target Price Alerts** - Get notified when price drops below your target
- **Dashboard** - View statistics, deals found, biggest price drops
- **Health Monitoring** - Detailed health checks for all services
- **Rate Limiting** - Brute force and spam protection
- **Request Logging** - All requests logged with duration tracking

## Tech Stack

- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15
- **Cache/Queue:** Redis 7
- **Authentication:** JWT + bcrypt
- **Containerization:** Docker & Docker Compose
- **Testing:** pytest

## Quick Start
```bash
git clone https://github.com/callmeouz/vastarion-hunter.git
cd vastarion-hunter
docker-compose up --build
```

API available at: http://localhost:8000
API docs (Swagger): http://localhost:8000/docs

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create new account |
| POST | /auth/login | Login and get JWT token |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /products/track | Add product to track |
| GET | /products/my-products | List tracked products |
| GET | /products/{id}/history | View price history |
| DELETE | /products/{id} | Stop tracking product |
| POST | /products/check-prices | Trigger price check |
| GET | /products/dashboard/stats | View dashboard stats |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API status |
| GET | /health | Detailed health check |

## Project Structure
```
vastarion-hunter/
├── backend/
│   ├── app/
│   │   ├── models/        # Database models (SQLAlchemy)
│   │   ├── schemas/       # Request/Response schemas (Pydantic)
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic (price checker)
│   │   ├── utils/         # Helpers (security, JWT)
│   │   ├── main.py        # App entry point
│   │   ├── config.py      # Settings
│   │   └── database.py    # DB connection
│   ├── tests/             # pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## Architecture

The system follows a service-oriented backend architecture.

Flow:

1. User submits a product URL
2. Product metadata is stored in PostgreSQL
3. A price check job is pushed into Redis queue
4. Worker service fetches product price
5. Price history is stored and compared with target price
6. If price drop detected → notification triggered

## Example Request

Track a product:

POST /products/track

```json
{
  "url": "https://example.com/product/123",
  "target_price": 199.99
}
```

## Security

- Password hashing using bcrypt
- JWT-based authentication
- Rate limiting to prevent brute-force attacks
- Input validation using Pydantic schemas

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://postgres:1234@db:5432/hunter_db |
| REDIS_URL | Redis connection | redis://redis:6379/0 |
| SECRET_KEY | JWT signing key | supersecretkey123 |

## Running Tests
```bash
docker-compose exec api pytest tests/ -v
```

## Roadmap

- [ ] Wishlist & tag system
- [ ] Email notifications
- [ ] Background worker (auto price check)
- [ ] Retry mechanism for failed price scraping
- [ ] Redis caching for dashboard metrics
- [ ] Admin endpoints for user management
- [ ] User profile management
- [ ] Password change endpoint
- [ ] Database migrations with Alembic
- [ ] Frontend (React)

## Author

Oğuzhan Yılmaz - [GitHub](https://github.com/callmeouz)