# API Documentation — DEVSQUAD MoMo Transactions API

Base URL: `http://localhost:8000`

## Authentication
All endpoints require **Basic Authentication**.
- Username: `devsquad`
- Password: `devsquadpass`

If credentials are missing or invalid, the API returns:
- `401 Unauthorized` with header `WWW-Authenticate: Basic realm="MoMo API"`

---

## Endpoints

### GET /transactions
List all transactions.

**Request**
