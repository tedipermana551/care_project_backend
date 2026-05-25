---
title: Care Project Backend
emoji: 🤰
colorFrom: pink
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Care Project Backend API

Django REST Framework backend for the Care pregnancy tracking app.

## API Endpoints

- `POST /api/auth/register/` — Register a new user
- `POST /api/auth/login/` — Login and get JWT tokens
- `POST /api/auth/logout/` — Logout (blacklist refresh token)
- `GET/POST /api/logs/` — Daily logs
- `GET/POST /api/appointments/` — Appointments
- `GET /api/stats/` — Statistics
- `GET /api/docs/` — Swagger UI

## Tech Stack

- Django 4.2 + Django REST Framework
- PostgreSQL (Supabase)
- JWT Authentication (SimpleJWT)