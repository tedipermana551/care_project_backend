# Care Project — API Documentation

**Framework:** Django REST Framework  
**Base URL:** `http://localhost:8000`  
**Auth:** JWT (Bearer Token via `djangorestframework-simplejwt`)  
**Interactive Docs:** `GET /api/docs/` (Swagger UI) · `GET /api/redoc/` (ReDoc)

---

## Table of Contents

1. [Response Format](#1-response-format)
2. [Authentication](#2-authentication)
3. [Profile](#3-profile)
4. [Daily Logs](#4-daily-logs)
5. [Pregnancy Status](#5-pregnancy-status)
6. [Appointments](#6-appointments)
7. [Statistics](#7-statistics)
8. [Data Models Reference](#8-data-models-reference)
9. [Endpoint Quick Reference](#9-endpoint-quick-reference)

---

## 1. Response Format

Every endpoint returns a consistent JSON envelope.

### Success
```json
{
  "success": true,
  "message": "Human-readable message",
  "data": { }
}
```

### Error
```json
{
  "success": false,
  "message": "Human-readable error",
  "errors": {
    "field_name": ["Validation detail here"]
  }
}
```

### HTTP Status Codes Used

| Code | Meaning |
|------|---------|
| `200` | OK — successful GET or PATCH |
| `201` | Created — successful POST |
| `400` | Bad Request — validation failed |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — authenticated but not permitted |
| `404` | Not Found — resource does not exist |

---

## 2. Authentication

**Base path:** `/api/auth/`  
All endpoints in this section are **public** (no token required).

---

### POST `/api/auth/register/`

Register a new user account. Returns JWT tokens immediately after registration.

**Request Body** `application/json`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `full_name` | string | ✅ | Max 150 chars. Split into first + last name internally |
| `email` | string | ✅ | Must be unique across all users |
| `password` | string | ✅ | Minimum 8 characters |
| `confirm_password` | string | ✅ | Must match `password` |

```json
{
  "full_name": "Siti Rahayu",
  "email": "siti@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123"
}
```

**Response `201`**
```json
{
  "success": true,
  "message": "Registration successful.",
  "data": {
    "user": {
      "id": 1,
      "full_name": "Siti Rahayu",
      "email": "siti@example.com"
    },
    "access": "<access_token>",
    "refresh": "<refresh_token>"
  }
}
```

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| Email already taken | `400` | `A user with this email already exists.` |
| Passwords don't match | `400` | `Passwords do not match.` |
| Password too short | `400` | Validation error on `password` |

---

### POST `/api/auth/login/`

Login with email and password. Returns fresh JWT tokens.

**Request Body** `application/json`

| Field | Type | Required |
|-------|------|----------|
| `email` | string | ✅ |
| `password` | string | ✅ |

```json
{
  "email": "siti@example.com",
  "password": "securepass123"
}
```

**Response `200`**
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "user": {
      "id": 1,
      "full_name": "Siti Rahayu",
      "email": "siti@example.com"
    },
    "access": "<access_token>",
    "refresh": "<refresh_token>"
  }
}
```

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| Wrong credentials | `401` | `Invalid email or password.` |
| Missing fields | `400` | `Email and password are required.` |

---

### POST `/api/auth/token/refresh/`

Exchange a refresh token for a new access token.

**Request Body** `application/json`

```json
{
  "refresh": "<refresh_token>"
}
```

**Response `200`**
```json
{
  "access": "<new_access_token>"
}
```

---

### POST `/api/auth/logout/`

🔒 **Requires auth**

Blacklists the refresh token so it can no longer be used.

**Request Body** `application/json`

```json
{
  "refresh": "<refresh_token>"
}
```

**Response `200`**
```json
{
  "success": true,
  "message": "Logged out successfully.",
  "data": null
}
```

---

## 3. Profile

**Base path:** `/api/profile/`  
🔒 All endpoints require authentication.

---

### POST `/api/profile/setup/`

Set the user's role and (for mothers) their pregnancy dates. This must be called once after registration before using most other features.

**Request Body** `application/json`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `role` | string | ✅ | `"mother"` or `"husband"` |
| `due_date` | date | ⚠️ | Required when `role` is `"mother"`. Format: `YYYY-MM-DD`. Must be a future date |
| `pregnancy_start_date` | date | ❌ | Format: `YYYY-MM-DD` |

```json
{
  "role": "mother",
  "due_date": "2026-11-15",
  "pregnancy_start_date": "2026-02-20"
}
```

**Response `201`** — returns the full profile object (see [Profile Object](#profile-object))

---

### GET `/api/profile/me/`

Return the authenticated user's full profile including all detail fields and avatar URL.

**Response `200`** — returns the full [Profile Object](#profile-object)

---

### PATCH `/api/profile/me/`

Update text-based profile fields. All fields are optional — send only what needs to change.

> ⚠️ **Do not use this endpoint to upload a profile picture.** Use `PATCH /api/profile/avatar/` instead (requires `multipart/form-data`).

**Request Body** `application/json` — all fields optional

| Field | Type | Notes |
|-------|------|-------|
| `nickname` | string | Max 50 chars. Send `""` to clear |
| `about` | string | Max 300 chars. Send `""` to clear |
| `due_date` | date | `YYYY-MM-DD`. Mother only |
| `pregnancy_start_date` | date | `YYYY-MM-DD` |

```json
{
  "nickname": "Mama Siti",
  "about": "28 weeks pregnant, based in Bandung."
}
```

**Response `200`** — returns the updated full [Profile Object](#profile-object)

---

### PATCH `/api/profile/avatar/`

Upload or replace the profile picture.

> Content-Type must be `multipart/form-data`.

**Request Body** `multipart/form-data`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `avatar` | file | ✅ | Accepted: `.jpg`, `.jpeg`, `.png`, `.webp`. Max size: **2 MB** |

**Response `200`**
```json
{
  "success": true,
  "message": "Profile picture updated successfully.",
  "data": {
    "avatar_url": "http://localhost:8000/media/avatars/1/a3f2b1cd.jpg"
  }
}
```

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| File exceeds 2 MB | `400` | `Image size must not exceed 2 MB.` |
| Unsupported file type | `400` | `Unsupported file type ".gif". Allowed types: .jpg, .jpeg, .png, .webp.` |
| No file attached | `400` | Validation error on `avatar` |
| Wrong Content-Type | `400` | Parser error |

---

### DELETE `/api/profile/avatar/`

Remove the current profile picture. The file is deleted from disk and `avatar_url` returns to `null`.

**Response `200`**
```json
{
  "success": true,
  "message": "Profile picture removed successfully.",
  "data": null
}
```

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| No avatar set | `404` | `No profile picture to remove.` |

---

### GET `/api/profile/my-code/`

Returns the user's unique pairing code. Share this code with a partner so they can link accounts.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "unique_code": "AB12CD34"
  }
}
```

---

### POST `/api/profile/link-partner/`

Link this account to a partner's account using their unique code. Roles must be complementary (`mother` ↔ `husband`). Both accounts must have completed profile setup first.

**Request Body** `application/json`

| Field | Type | Required |
|-------|------|----------|
| `code` | string | ✅ |

```json
{
  "code": "XY34WZ12"
}
```

**Response `200`** — returns the current user's updated profile

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| Code not found | `404` | `No user found with that code.` |
| Linking to self | `400` | `You cannot link with yourself.` |
| Already linked | `400` | `You are already linked to a partner.` |
| Same role | `400` | `Partner must have a complementary role (mother ↔ husband).` |
| Role not set | `400` | `Both users must set their role before linking.` |

---

### DELETE `/api/profile/unlink-partner/`

Remove the partner link from both accounts simultaneously.

**Response `200`**
```json
{
  "success": true,
  "message": "Partner unlinked successfully.",
  "data": null
}
```

---

### Profile Object

Returned by `GET /api/profile/me/`, `POST /api/profile/setup/`, and `PATCH /api/profile/me/`.

```json
{
  "id": 1,
  "full_name": "Siti Rahayu",
  "email": "siti@example.com",
  "role": "mother",
  "unique_code": "AB12CD34",
  "nickname": "Mama Siti",
  "about": "28 weeks pregnant, based in Bandung.",
  "avatar_url": "http://localhost:8000/media/avatars/1/a3f2b1cd.jpg",
  "due_date": "2026-11-15",
  "pregnancy_start_date": "2026-02-20",
  "created_at": "2026-01-01T08:00:00Z",
  "updated_at": "2026-05-10T14:30:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Profile ID |
| `full_name` | string | Derived from user's first + last name |
| `email` | string | From the user account |
| `role` | string | `"mother"` or `"husband"` |
| `unique_code` | string | 8-char alphanumeric. Read-only |
| `nickname` | string | Optional display name. Empty string if not set |
| `about` | string | Optional bio. Empty string if not set |
| `avatar_url` | string \| null | Absolute URL to profile picture. `null` if not uploaded |
| `due_date` | date \| null | Baby's due date. Mothers only |
| `pregnancy_start_date` | date \| null | First day of pregnancy |
| `created_at` | datetime | ISO 8601. Read-only |
| `updated_at` | datetime | ISO 8601. Read-only |

---

## 4. Daily Logs

**Base path:** `/api/logs/`  
🔒 All endpoints require authentication.

---

### POST `/api/logs/`

Create a daily log entry. Only **one log per user per day** is allowed.

**Request Body** `application/json`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `date` | date | ❌ | Defaults to today. Format: `YYYY-MM-DD` |
| `mood` | string | ✅ | One of: `great`, `good`, `neutral`, `bad`, `terrible` |
| `complaints` | string | ❌ | Free text. Defaults to `""` |
| `sleep_duration` | decimal | ✅ | Hours slept. Range: `0–24` |
| `exercise_duration` | decimal | ✅ | Minutes exercised. Range: `0–1440` |
| `notes` | string | ❌ | Free text. Defaults to `""` |
| `partner_message` | string | ❌ | Short message for partner. Max **280 chars**. Defaults to `""` |

```json
{
  "date": "2026-05-20",
  "mood": "good",
  "complaints": "Some back pain in the morning.",
  "sleep_duration": 7.5,
  "exercise_duration": 20,
  "notes": "Drank more water today.",
  "partner_message": "Baby kicked a lot today! Can't wait for you to feel it."
}
```

**Response `201`** — returns the created [Log Object](#log-object)

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| Log already exists for that date | `400` | `A log for YYYY-MM-DD already exists.` |
| Invalid mood value | `400` | Validation error |
| sleep_duration out of range | `400` | `sleep_duration must be between 0 and 24 hours.` |
| partner_message over 280 chars | `400` | Validation error on `partner_message` |

---

### GET `/api/logs/`

Return all logs for the authenticated user, newest first.

**Query Parameters** — all optional

| Param | Type | Example | Description |
|-------|------|---------|-------------|
| `start_date` | date | `2026-01-01` | Filter logs on or after this date |
| `end_date` | date | `2026-05-31` | Filter logs on or before this date |
| `mood` | string | `good` | Filter by a specific mood |
| `month` | string | `2026-03` | Filter by year-month |

**Response `200`** — returns array of [Log Objects](#log-object)

---

### GET `/api/logs/today/`

Shortcut to get today's log entry.

**Response `200`** — returns a single [Log Object](#log-object)

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| No log exists for today | `404` | `No log found for today.` |

---

### GET `/api/logs/<log_date>/`

Get the log for a specific date.

**Path Parameter:** `log_date` — format `YYYY-MM-DD`

**Response `200`** — returns a single [Log Object](#log-object)

---

### PATCH `/api/logs/<log_date>/`

Update any field of an existing log. Partial updates are supported — send only what needs to change.

**Path Parameter:** `log_date` — format `YYYY-MM-DD`

```json
{
  "partner_message": "She kicked again at 9pm! I counted 10 times."
}
```

**Response `200`** — returns the updated [Log Object](#log-object)

---

### DELETE `/api/logs/<log_date>/`

Delete a log for a specific date.

**Path Parameter:** `log_date` — format `YYYY-MM-DD`

**Response `200`**
```json
{
  "success": true,
  "message": "Log deleted successfully.",
  "data": null
}
```

---

### GET `/api/logs/partner/`

🔗 **Requires linked partner**

Read the linked partner's full log history. Supports the same query params as `GET /api/logs/`. Response includes `partner_message`, `has_message`, and sender info fields.

**Response `200`** — returns array of [Partner Log Objects](#partner-log-object)

---

### GET `/api/logs/partner/messages/`

🔗 **Requires linked partner**

Returns **only** the partner's logs that contain a `partner_message`. Useful for building an inbox or notification view. Ordered newest first.

**Query Parameters** — same date filters as `GET /api/logs/`

**Response `200`** — returns array of [Partner Log Objects](#partner-log-object)

```json
{
  "success": true,
  "message": "2 message(s) found.",
  "data": [...]
}
```

---

### Log Object

```json
{
  "id": 5,
  "date": "2026-05-20",
  "mood": "good",
  "complaints": "Some back pain.",
  "sleep_duration": "7.5",
  "exercise_duration": "20.0",
  "notes": "Drank more water today.",
  "partner_message": "Baby kicked a lot today!",
  "created_at": "2026-05-20T08:00:00Z",
  "updated_at": "2026-05-20T21:00:00Z"
}
```

### Partner Log Object

Same as Log Object but adds three read-only fields:

```json
{
  "id": 5,
  "date": "2026-05-20",
  "mood": "good",
  "complaints": "Some back pain.",
  "sleep_duration": "7.5",
  "exercise_duration": "20.0",
  "notes": "Drank more water today.",
  "partner_message": "Baby kicked a lot today!",
  "has_message": true,
  "sender_display_name": "Mama Siti",
  "sender_nickname": "Mama Siti",
  "created_at": "2026-05-20T08:00:00Z",
  "updated_at": "2026-05-20T21:00:00Z"
}
```

| Extra Field | Type | Notes |
|-------------|------|-------|
| `has_message` | boolean | `true` if `partner_message` is non-empty. Use for notification badges |
| `sender_display_name` | string | Nickname if set, otherwise full name |
| `sender_nickname` | string | Raw nickname value. Empty string if not set |

---

## 5. Pregnancy Status

**Base path:** `/api/pregnancy/`  
🔒 Requires authentication. Both the mother and a linked husband can access this endpoint.

---

### GET `/api/pregnancy/status/`

Returns real-time calculated pregnancy progress based on the mother's `due_date` and `pregnancy_start_date`. If called by the husband, it automatically reads from the linked wife's profile.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "due_date": "2026-11-15",
    "pregnancy_start_date": "2026-02-20",
    "days_pregnant": 89,
    "weeks_pregnant": 12,
    "trimester": 1,
    "days_until_due": 179,
    "weeks_until_due": 25,
    "progress_percentage": 33.2,
    "is_overdue": false
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `days_pregnant` | integer | Days since `pregnancy_start_date` |
| `weeks_pregnant` | integer | `days_pregnant ÷ 7` |
| `trimester` | integer | `1` (weeks 1–12), `2` (weeks 13–26), `3` (weeks 27+) |
| `days_until_due` | integer | `0` if overdue |
| `weeks_until_due` | integer | `0` if overdue |
| `progress_percentage` | float | Percentage of total pregnancy elapsed |
| `is_overdue` | boolean | `true` if today is past `due_date` |

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| No mother profile found | `404` | `No pregnancy data found. Link to a mother profile.` |
| `due_date` not set | `404` | `Due date is not set.` |
| `pregnancy_start_date` not set | `404` | `Pregnancy start date is not set.` |

---

## 6. Appointments

**Base path:** `/api/appointments/`  
🔒 All endpoints require authentication.

---

### POST `/api/appointments/`

Create a new doctor appointment.

**Request Body** `application/json`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | ✅ | Max 200 chars |
| `doctor_name` | string | ✅ | Max 150 chars |
| `appointment_date` | datetime | ✅ | ISO 8601. Must be a **future** date/time |
| `location` | string | ❌ | Max 150 chars |
| `notes` | string | ❌ | Free text |
| `reminder_days_before` | integer | ❌ | Default: `1`. Must be `≥ 0` |

```json
{
  "title": "Second Trimester Check-Up",
  "doctor_name": "Dr. Ayu Pratiwi",
  "location": "RS Hermina Bandung",
  "appointment_date": "2026-06-10T09:00:00Z",
  "notes": "Bring previous ultrasound results.",
  "reminder_days_before": 2
}
```

**Response `201`** — returns the created [Appointment Object](#appointment-object)

**Error cases**

| Condition | Status | Message |
|-----------|--------|---------|
| `appointment_date` in the past (on create) | `400` | `Appointment date must be in the future.` |
| Negative `reminder_days_before` | `400` | Validation error |

---

### GET `/api/appointments/`

Return all appointments for the authenticated user, ordered by `appointment_date` ascending.

**Response `200`** — returns array of [Appointment Objects](#appointment-object)

---

### GET `/api/appointments/upcoming/`

Return only future, incomplete appointments. Ordered by `appointment_date` ascending.

**Response `200`** — returns array of [Appointment Objects](#appointment-object)

---

### GET `/api/appointments/<id>/`

Get a single appointment by ID.

**Response `200`** — returns a single [Appointment Object](#appointment-object)

---

### PATCH `/api/appointments/<id>/`

Update an appointment. All fields optional. Partial updates supported.

> Note: `appointment_date` validation is skipped on update so you can edit other fields on past appointments without errors.

**Response `200`** — returns the updated [Appointment Object](#appointment-object)

---

### DELETE `/api/appointments/<id>/`

Delete an appointment permanently.

**Response `200`**
```json
{
  "success": true,
  "message": "Appointment deleted successfully.",
  "data": null
}
```

---

### PATCH `/api/appointments/<id>/complete/`

Mark an appointment as completed. Sets `is_completed` to `true`.

**Response `200`** — returns the updated [Appointment Object](#appointment-object)

---

### GET `/api/appointments/partner/`

🔗 **Requires linked partner**

Read-only view of the linked partner's appointment list.

**Response `200`** — returns array of [Appointment Objects](#appointment-object)

---

### Appointment Object

```json
{
  "id": 3,
  "title": "Second Trimester Check-Up",
  "doctor_name": "Dr. Ayu Pratiwi",
  "location": "RS Hermina Bandung",
  "appointment_date": "2026-06-10T09:00:00Z",
  "notes": "Bring previous ultrasound results.",
  "is_completed": false,
  "reminder_days_before": 2,
  "created_at": "2026-05-01T10:00:00Z"
}
```

---

## 7. Statistics

**Base path:** `/api/stats/`  
🔒 All endpoints require authentication. All data is scoped to the authenticated user's own logs only.

### Shared Query Parameters

All stats endpoints accept these optional query params:

| Param | Type | Example | Description |
|-------|------|---------|-------------|
| `start_date` | date | `2026-01-01` | Filter logs on or after |
| `end_date` | date | `2026-05-31` | Filter logs on or before |
| `period` | string | `weekly` or `monthly` | Auto-sets date range. `weekly` = last 7 days, `monthly` = current month. Ignored if `start_date`/`end_date` are provided |

---

### GET `/api/stats/summary/`

Returns an overall summary of all daily log data.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "total_logs": 45,
    "logging_streak_days": 7,
    "average_sleep_hours": 7.4,
    "average_exercise_minutes": 22.5,
    "most_common_mood": "good",
    "mood_distribution": {
      "great": 10,
      "good": 20,
      "neutral": 8,
      "bad": 5,
      "terrible": 2
    },
    "period": {
      "start": "2026-01-01",
      "end": "2026-05-20"
    }
  }
}
```

---

### GET `/api/stats/mood/`

Returns mood distribution counts and a day-by-day mood timeline. Ideal for rendering mood charts on the frontend.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "mood_distribution": {
      "great": 10,
      "good": 20,
      "neutral": 8,
      "bad": 5,
      "terrible": 2
    },
    "timeline": [
      { "date": "2026-05-01", "mood": "good" },
      { "date": "2026-05-02", "mood": "great" }
    ],
    "period": { "start": "2026-05-01", "end": "2026-05-20" }
  }
}
```

---

### GET `/api/stats/sleep/`

Returns average sleep duration and a day-by-day sleep timeline. Ideal for line/bar charts.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "average_sleep_hours": 7.4,
    "timeline": [
      { "date": "2026-05-01", "sleep_duration": "7.5" },
      { "date": "2026-05-02", "sleep_duration": "8.0" }
    ],
    "period": { "start": "2026-05-01", "end": "2026-05-20" }
  }
}
```

---

### GET `/api/stats/exercise/`

Returns average exercise duration and a day-by-day exercise timeline.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "average_exercise_minutes": 22.5,
    "timeline": [
      { "date": "2026-05-01", "exercise_duration": "20.0" },
      { "date": "2026-05-02", "exercise_duration": "30.0" }
    ],
    "period": { "start": "2026-05-01", "end": "2026-05-20" }
  }
}
```

---

### GET `/api/stats/streaks/`

Returns logging streak information. Does **not** support date filter params — always computed from the full log history.

**Response `200`**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "current_streak": 7,
    "longest_streak_days": 21,
    "total_logged_days": 45,
    "last_logged_date": "2026-05-20"
  }
}
```

| Field | Notes |
|-------|-------|
| `current_streak` | Consecutive days logged up to today |
| `longest_streak_days` | Longest ever consecutive streak |
| `total_logged_days` | Total unique days with a log entry |
| `last_logged_date` | Most recent log date. `null` if no logs exist |

---

## 8. Data Models Reference

### UserProfile

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `role` | `"mother"` \| `"husband"` | `""` | Set via `/profile/setup/` |
| `unique_code` | string | auto | 8-char alphanumeric. Auto-generated. Read-only |
| `partner` | UserProfile | `null` | Linked via `/profile/link-partner/` |
| `due_date` | date | `null` | Mother only |
| `pregnancy_start_date` | date | `null` | |
| `nickname` | string | `""` | Max 50 chars. Optional |
| `about` | string | `""` | Max 300 chars. Optional |
| `avatar` | image | `null` | Stored at `media/avatars/<user_id>/<uuid>.ext` |

### DailyLog

| Field | Type | Notes |
|-------|------|-------|
| `date` | date | Unique per user per day |
| `mood` | string | `great`, `good`, `neutral`, `bad`, `terrible` |
| `complaints` | string | Optional |
| `sleep_duration` | decimal | Hours. Range 0–24 |
| `exercise_duration` | decimal | Minutes. Range 0–1440 |
| `notes` | string | Optional |
| `partner_message` | string | Max 280 chars. Optional |

### Appointment

| Field | Type | Notes |
|-------|------|-------|
| `title` | string | Max 200 chars |
| `doctor_name` | string | Max 150 chars |
| `location` | string | Optional |
| `appointment_date` | datetime | Must be future on create |
| `notes` | string | Optional |
| `is_completed` | boolean | Default `false` |
| `reminder_days_before` | integer | Default `1` |

---

## 9. Endpoint Quick Reference

### 🔓 Public (no token needed)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register/` | Register new account |
| `POST` | `/api/auth/login/` | Login, receive tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh access token |

### 🔒 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/logout/` | Blacklist refresh token |

### 🔒 Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/profile/setup/` | Set role + pregnancy dates |
| `GET` | `/api/profile/me/` | View own profile |
| `PATCH` | `/api/profile/me/` | Edit nickname, about, dates |
| `PATCH` | `/api/profile/avatar/` | Upload / replace profile picture |
| `DELETE` | `/api/profile/avatar/` | Remove profile picture |
| `GET` | `/api/profile/my-code/` | Get pairing code |
| `POST` | `/api/profile/link-partner/` | Link to partner by code |
| `DELETE` | `/api/profile/unlink-partner/` | Unlink from partner |

### 🔒 Daily Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/logs/` | Create today's log |
| `GET` | `/api/logs/` | List all logs (with filters) |
| `GET` | `/api/logs/today/` | Get today's log |
| `GET` | `/api/logs/<date>/` | Get log for specific date |
| `PATCH` | `/api/logs/<date>/` | Update log for specific date |
| `DELETE` | `/api/logs/<date>/` | Delete log for specific date |
| `GET` | `/api/logs/partner/` | View partner's all logs |
| `GET` | `/api/logs/partner/messages/` | View partner's logs with messages only |

### 🔒 Pregnancy

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/pregnancy/status/` | Real-time pregnancy countdown |

### 🔒 Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/appointments/` | Create appointment |
| `GET` | `/api/appointments/` | List all appointments |
| `GET` | `/api/appointments/upcoming/` | List upcoming appointments |
| `GET` | `/api/appointments/<id>/` | Get single appointment |
| `PATCH` | `/api/appointments/<id>/` | Update appointment |
| `DELETE` | `/api/appointments/<id>/` | Delete appointment |
| `PATCH` | `/api/appointments/<id>/complete/` | Mark as completed |
| `GET` | `/api/appointments/partner/` | View partner's appointments |

### 🔒 Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats/summary/` | Overall log summary |
| `GET` | `/api/stats/mood/` | Mood distribution + timeline |
| `GET` | `/api/stats/sleep/` | Sleep average + timeline |
| `GET` | `/api/stats/exercise/` | Exercise average + timeline |
| `GET` | `/api/stats/streaks/` | Logging streak info |

### 📖 API Docs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/docs/` | Swagger UI |
| `GET` | `/api/redoc/` | ReDoc UI |
| `GET` | `/api/schema/` | Raw OpenAPI schema (JSON) |

---

*Last updated: May 2026 — includes profile details (nickname, about, avatar), partner message on daily logs.*