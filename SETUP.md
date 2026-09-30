# Data Intelligence Suite - Backend Setup Guide

## Quick Start

### Option 1: Virtual Environment (Development)

```bash
# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server runs on `http://localhost:8000`

### Option 2: Docker (Production)

```bash
# Build and run
docker-compose up --build

# Server runs on http://localhost:8000
```

---

## Database Configuration

### PostgreSQL

```bash
# Connection in frontend or via API:
{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "username": "postgres",
  "password": "password",
  "database": "data_intelligence"
}
```

### MySQL

```bash
{
  "db_type": "mysql",
  "host": "localhost",
  "port": 3306,
  "username": "root",
  "password": "password",
  "database": "data_intelligence"
}
```

---

## API Endpoints

### Health Check
```
GET http://localhost:8000/api/health
```

### Connect Database
```
POST http://localhost:8000/api/connect
Content-Type: application/json

{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "username": "postgres",
  "password": "password",
  "database": "your_database"
}
```

### Get Schema
```
GET http://localhost:8000/api/schema
```

### Execute Query
```
POST http://localhost:8000/api/query
Content-Type: application/json

{
  "query": "Show me top 10 employees by salary",
  "limit": 100
}
```

Response:
```json
{
  "generated_sql": "SELECT * FROM employees ORDER BY salary DESC LIMIT 10",
  "results": [...],
  "rows_affected": 10,
  "execution_time": 0.25,
  "confidence": 0.95
}
```

### Upload CSV
```
POST http://localhost:8000/api/upload
Content-Type: multipart/form-data

[file: data.csv]
```

---

## MiniLM v6 Setup

The backend automatically uses MiniLM v6 if available:

```bash
# Install sentence-transformers (in venv)
pip install sentence-transformers

# First run will download the model (~450MB)
python main.py
```

If not installed, falls back to token-based similarity matching.

---

## Environment Variables

```bash
# .env file
PORT=8000
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=password
DB_NAME=data_intelligence
```

---

## Troubleshooting

**ImportError: No module named 'sqlalchemy'**
```bash
pip install -r requirements.txt
```

**Connection refused**
- Check database is running
- Verify host/port/credentials

**MiniLM model slow on first run**
- Normal — downloads ~450MB on first execution
- Cached after first run

**CORS errors**
- Frontend and backend must be on different origins
- CORS is already enabled in FastAPI app
